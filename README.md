# YT-Tutor: AI-Powered YouTube Video Tutor

An intelligent tutoring system that extracts transcripts from YouTube videos and allows you to ask questions about the content using AI. Perfect for students, researchers, and anyone looking to better understand video lectures and educational content.

<img width="1001" height="839" alt="YT-Tutor" src="https://github.com/user-attachments/assets/298f4f8e-9b34-4a00-9625-bfef6c76f83f" />

## Features

- **YouTube Transcript Extraction**: Automatically fetches English transcripts from YouTube videos
- **AI-Powered Q&A**: Ask questions about video content and get intelligent answers
- **Vector Search**: Uses semantic search to find relevant transcript segments
- **User-Friendly Interface**: Clean Streamlit web interface
- **Error Handling**: Comprehensive error handling for various transcript issues

## How It Works

1. Enter a YouTube video URL
2. The app extracts the transcript and processes it into searchable chunks
3. Ask questions about the video content
4. Get AI-powered answers based on the transcript

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Groq API key (free tier available)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd yt-tutor
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file in the project root and add your Groq API key:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

To get a free Groq API key:
- Visit [Groq Console](https://console.groq.com/)
- Sign up for a free account
- Navigate to API Keys and create a new key

## Usage

1. Start the application:
```bash
uv run streamlit run main.py
```

2. Open your browser and navigate to the displayed URL (typically `http://localhost:8501`)

3. Enter a YouTube video URL and click "Fetch Transcript"

4. Once the transcript is processed, ask questions about the video content

## Dependencies

- **streamlit**: Web interface framework
- **pytube**: YouTube video information extraction
- **youtube-transcript-api**: Transcript fetching from YouTube
- **langchain**: LLM orchestration framework
- **langchain-groq**: Groq LLM integration
- **langchain-huggingface**: HuggingFace embeddings integration
- **faiss-cpu**: Vector similarity search
- **sentence-transformers**: Text embeddings
- **python-dotenv**: Environment variable management

## Supported Video Types

- Videos with English transcripts (auto-generated or manual)
- Public YouTube videos
- Videos with transcripts enabled

## Limitations

- Only supports English transcripts
- Requires videos to have transcripts available
- Depends on YouTube's transcript API availability
- LLM responses are limited by the quality of the transcript

## Error Handling

The application handles various common issues:
- Transcripts disabled for video
- No English transcript available
- Video unavailable or private
- Network connectivity issues
- Invalid YouTube URLs

## Testing

The project includes comprehensive unit tests covering all core functionality.

### Running Tests

**Basic test run:**
```bash
uv run pytest tests/ -v
```

**With coverage report:**
```bash
uv run pytest tests/ --cov=main --cov-report=term-missing
```

**Using the test runner script:**
```bash
# Basic tests
python test_runner.py

# With coverage
python test_runner.py --coverage
```

### Test Coverage

The test suite covers:
- URL parsing and video ID extraction
- Video title fetching (with fallback methods)
- Transcript saving and loading
- Error handling for various YouTube API issues
- Path injection protection

Current test coverage: ~67% of main functionality

### Writing Tests

When contributing new features:
1. Add tests for new functions in `tests/test_main.py`
2. Use pytest fixtures and mocking for external dependencies
3. Test both success and failure scenarios
4. Ensure tests are independent and can run in any order

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `python test_runner.py --coverage`
6. Ensure all tests pass and maintain good coverage
7. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions:
1. Check the error messages in the app interface
2. Ensure your Groq API key is valid
3. Verify the YouTube video has transcripts available
4. Open an issue on GitHub for bugs or feature requests

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Powered by [Groq](https://groq.com/) for fast LLM inference
- Uses [LangChain](https://langchain.com/) for LLM orchestration
- Transcript extraction via [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api)
