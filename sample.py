import re
import requests
from urllib.parse import urlparse, parse_qs
from pytube import YouTube

def get_video_id_from_url(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path[:7] == '/embed/':
            return parsed_url.path.split('/')[2]
        elif parsed_url.path[:3] == '/v/':
            return parsed_url.path.split('/')[2]
    return None

def get_title_via_api(video_id):
    """Get video title using YouTube's oEmbed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('title', 'Unknown Title')
    except Exception as e:
        print(f"oEmbed API failed: {e}")
    return None

def get_title_via_scraping(url):
    """Get video title by scraping the YouTube page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Look for the title in the page content
            title_match = re.search(r'"title":"([^"]+)"', response.text)
            if title_match:
                title = title_match.group(1)
                # Decode unicode escapes
                title = title.encode().decode('unicode_escape')
                return title
    except Exception as e:
        print(f"Scraping failed: {e}")
    return None

def get_title_via_pytube(url):
    """Get video title using pytube"""
    try:
        yt = YouTube(url)
        return yt.title
    except Exception as e:
        print(f"Pytube failed: {e}")
    return None

def get_video_title(url):
    """Try multiple methods to get video title"""
    print(f"Attempting to get title for: {url}")
    
    # Method 1: Try pytube first
    title = get_title_via_pytube(url)
    if title:
        print(f"✓ Pytube method worked: {title}")
        return title
    
    # Method 2: Try oEmbed API
    video_id = get_video_id_from_url(url)
    if video_id:
        title = get_title_via_api(video_id)
        if title:
            print(f"✓ oEmbed API method worked: {title}")
            return title
    
    # Method 3: Try scraping
    title = get_title_via_scraping(url)
    if title:
        print(f"✓ Scraping method worked: {title}")
        return title
    
    print("✗ All methods failed")
    return "Unknown Title"

# Test with a sample YouTube URL
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=rkvECjsVT6g&t=2155s"  # Your test URL
    title = get_video_title(test_url)
    print(f"\nFinal result: {title}")
