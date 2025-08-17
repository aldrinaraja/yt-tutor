import pytest
import os
import tempfile
import requests
from unittest.mock import patch, Mock, mock_open
from urllib.parse import parse_qs

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import (
    get_video_id_from_url,
    get_video_title,
    save_transcript_to_file,
    get_video_transcript
)


class TestGetVideoIdFromUrl:
    """Test the video ID extraction function"""
    
    def test_youtube_watch_url(self):
        """Test standard YouTube watch URL"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert get_video_id_from_url(url) == "dQw4w9WgXcQ"
    
    def test_youtube_watch_url_with_params(self):
        """Test YouTube URL with additional parameters"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s"
        assert get_video_id_from_url(url) == "dQw4w9WgXcQ"
    
    def test_youtu_be_short_url(self):
        """Test shortened youtu.be URL"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert get_video_id_from_url(url) == "dQw4w9WgXcQ"
    
    def test_embed_url(self):
        """Test YouTube embed URL"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert get_video_id_from_url(url) == "dQw4w9WgXcQ"
    
    def test_v_url(self):
        """Test YouTube /v/ URL format"""
        url = "https://www.youtube.com/v/dQw4w9WgXcQ"
        assert get_video_id_from_url(url) == "dQw4w9WgXcQ"
    
    def test_invalid_url(self):
        """Test invalid URL returns None"""
        url = "https://example.com/video"
        assert get_video_id_from_url(url) is None
    
    def test_youtube_url_without_video_id(self):
        """Test YouTube URL without video ID"""
        url = "https://www.youtube.com/"
        assert get_video_id_from_url(url) is None


class TestGetVideoTitle:
    """Test the video title fetching function"""
    
    @patch('main.YouTube')
    def test_pytube_success(self, mock_youtube):
        """Test successful title fetch using pytube"""
        mock_yt = Mock()
        mock_yt.title = "Test Video Title"
        mock_youtube.return_value = mock_yt
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = get_video_title(url)
        
        assert title == "Test Video Title"
        mock_youtube.assert_called_once_with(url)
    
    @patch('main.requests.get')
    @patch('main.get_video_id_from_url')
    @patch('main.YouTube')
    def test_oembed_fallback_success(self, mock_youtube, mock_get_id, mock_requests):
        """Test successful title fetch using oEmbed API fallback"""
        # Make pytube fail
        mock_youtube.side_effect = Exception("Pytube failed")
        
        # Mock video ID extraction
        mock_get_id.return_value = "dQw4w9WgXcQ"
        
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"title": "API Fetched Title"}
        mock_requests.return_value = mock_response
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = get_video_title(url)
        
        assert title == "API Fetched Title"
        mock_requests.assert_called_once()
    
    @patch('main.requests.get')
    @patch('main.get_video_id_from_url')
    @patch('main.YouTube')
    def test_all_methods_fail(self, mock_youtube, mock_get_id, mock_requests):
        """Test when all title fetching methods fail"""
        # Make pytube fail
        mock_youtube.side_effect = Exception("Pytube failed")
        
        # Make video ID extraction fail
        mock_get_id.return_value = None
        
        url = "https://www.youtube.com/watch?v=invalid"
        title = get_video_title(url)
        
        assert title == "Unknown Title"
    
    @patch('main.requests.get')
    @patch('main.get_video_id_from_url')
    @patch('main.YouTube')
    def test_oembed_api_error(self, mock_youtube, mock_get_id, mock_requests):
        """Test oEmbed API returning error status"""
        # Make pytube fail
        mock_youtube.side_effect = Exception("Pytube failed")
        
        # Mock video ID extraction
        mock_get_id.return_value = "dQw4w9WgXcQ"
        
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.return_value = mock_response
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        title = get_video_title(url)
        
        assert title == "Unknown Title"


class TestSaveTranscriptToFile:
    """Test the transcript saving function"""
    
    def test_save_transcript_success(self):
        """Test successful transcript saving"""
        transcript = "This is a test transcript content."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            temp_filename = tmp_file.name
        
        try:
            # Use just the filename part for the function
            filename = os.path.basename(temp_filename)
            save_transcript_to_file(transcript, filename)
            
            # Read back the content
            with open(filename, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            assert saved_content == transcript
            
            # Clean up
            os.unlink(filename)
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def test_save_transcript_default_filename(self):
        """Test saving with default filename"""
        transcript = "Default filename test content."
        
        try:
            save_transcript_to_file(transcript)
            
            # Check if file was created with default name
            assert os.path.exists("transcript.txt")
            
            with open("transcript.txt", 'r', encoding='utf-8') as f:
                saved_content = f.read()
            
            assert saved_content == transcript
            
        finally:
            if os.path.exists("transcript.txt"):
                os.unlink("transcript.txt")
    
    def test_save_transcript_invalid_extension(self):
        """Test error when using invalid file extension"""
        transcript = "Test content"
        
        with pytest.raises(ValueError, match="Invalid file extension"):
            save_transcript_to_file(transcript, "test.pdf")
    
    def test_save_transcript_path_injection_protection(self):
        """Test protection against path injection"""
        transcript = "Test content"
        
        # Try to save to a different directory
        filename = "../dangerous_file.txt"
        save_transcript_to_file(transcript, filename)
        
        # Should save as just the basename
        assert os.path.exists("dangerous_file.txt")
        assert not os.path.exists("../dangerous_file.txt")
        
        # Clean up
        if os.path.exists("dangerous_file.txt"):
            os.unlink("dangerous_file.txt")


class TestGetVideoTranscript:
    """Test the transcript fetching function"""
    
    @patch('main.YouTubeTranscriptApi')
    @patch('main.YouTube')
    def test_get_transcript_success(self, mock_youtube, mock_transcript_api):
        """Test successful transcript fetching"""
        # Mock YouTube object
        mock_yt = Mock()
        mock_yt.video_id = "dQw4w9WgXcQ"
        mock_youtube.return_value = mock_yt
        
        # Mock transcript data
        mock_transcript_list = Mock()
        mock_transcript_data = Mock()
        mock_transcript_data.fetch.return_value = [
            Mock(text="Hello"),
            Mock(text="world"),
            Mock(text="test")
        ]
        mock_transcript_list.find_transcript.return_value = mock_transcript_data
        mock_transcript_api.return_value.list.return_value = mock_transcript_list
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript = get_video_transcript(url)
        
        assert transcript == "Hello world test"
    
    @patch('main.YouTubeTranscriptApi')
    @patch('main.YouTube')
    def test_get_transcript_no_transcript_found(self, mock_youtube, mock_transcript_api):
        """Test when no transcript is found"""
        from youtube_transcript_api import NoTranscriptFound
        
        mock_yt = Mock()
        mock_yt.video_id = "dQw4w9WgXcQ"
        mock_youtube.return_value = mock_yt
        
        mock_transcript_api.return_value.list.side_effect = NoTranscriptFound(
            "dQw4w9WgXcQ", [], "No transcript found"
        )
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript = get_video_transcript(url)
        
        assert transcript is None
    
    @patch('main.YouTubeTranscriptApi')
    @patch('main.YouTube')
    def test_get_transcript_transcripts_disabled(self, mock_youtube, mock_transcript_api):
        """Test when transcripts are disabled"""
        from youtube_transcript_api import TranscriptsDisabled
        
        mock_yt = Mock()
        mock_yt.video_id = "dQw4w9WgXcQ"
        mock_youtube.return_value = mock_yt
        
        mock_transcript_api.return_value.list.side_effect = TranscriptsDisabled(
            "dQw4w9WgXcQ"
        )
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript = get_video_transcript(url)
        
        assert transcript is None
    
    @patch('main.YouTubeTranscriptApi')
    @patch('main.YouTube')
    def test_get_transcript_video_unavailable(self, mock_youtube, mock_transcript_api):
        """Test when video is unavailable"""
        from youtube_transcript_api import VideoUnavailable
        
        mock_youtube.side_effect = VideoUnavailable("dQw4w9WgXcQ")
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript = get_video_transcript(url)
        
        assert transcript is None
    
    @patch('main.YouTubeTranscriptApi')
    @patch('main.YouTube')
    def test_get_transcript_generic_exception(self, mock_youtube, mock_transcript_api):
        """Test handling of generic exceptions"""
        mock_youtube.side_effect = Exception("Generic error")
        
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        transcript = get_video_transcript(url)
        
        assert transcript is None


if __name__ == "__main__":
    pytest.main([__file__])