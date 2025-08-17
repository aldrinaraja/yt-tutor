import os
import re
import requests
from urllib.parse import urlparse, parse_qs
from pytube import YouTube
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)
import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_groq import ChatGroq

# Load environment variables from .env file
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


def get_video_id_from_url(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    elif parsed_url.hostname in ("www.youtube.com", "youtube.com"):
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query)["v"][0]
        elif parsed_url.path[:7] == "/embed/":
            return parsed_url.path.split("/")[2]
        elif parsed_url.path[:3] == "/v/":
            return parsed_url.path.split("/")[2]
    return None


def get_video_title(url):
    """Get video title using multiple fallback methods"""
    try:
        # Method 1: Try pytube first
        yt = YouTube(url)
        return yt.title
    except Exception:
        pass

    try:
        # Method 2: Try oEmbed API as fallback
        video_id = get_video_id_from_url(url)
        if video_id:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = requests.get(oembed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("title", "Unknown Title")
    except Exception:
        pass

    return "Unknown Title"


def get_video_transcript(url):
    """
    Fetches the English transcript for a given YouTube video URL.
    Returns the transcript text or None if not available.
    Displays user-friendly error messages for common issues.
    """
    try:
        video_id = YouTube(url).video_id
        # Get available transcripts for the video
        transcript_list = YouTubeTranscriptApi().list(video_id)
        # Find the English transcript
        transcript_data = transcript_list.find_transcript(["en"])
        # Combine transcript segments into a single string
        text = " ".join([item.text for item in transcript_data.fetch()])
        return text
    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video. Please try another video.")
        return None
    except NoTranscriptFound:
        st.error(
            "No English transcript found for this video. Please try another video."
        )
        return None
    except VideoUnavailable:
        st.error("The video is unavailable. Please check the URL or try another video.")
        return None
    except CouldNotRetrieveTranscript:
        st.error(
            "Could not retrieve the transcript due to a network or API issue. Please try again later."
        )
        return None
    except Exception as e:
        st.error(
            "An unexpected error occurred. Please check the video URL and try again."
        )
        return None


def save_transcript_to_file(transcript, filename="transcript.txt"):
    """
    Saves the transcript text to a local file.
    Ensures the filename is safe to prevent path injection.
    """
    safe_filename = os.path.basename(filename)
    # Only allow .txt files
    if not safe_filename.endswith(".txt"):
        raise ValueError("Invalid file extension. Only .txt files are allowed.")
    with open(safe_filename, "w", encoding="utf-8") as f:
        f.write(transcript)


# Streamlit UI setup
st.title("AI Powered Tutor")
st.write("Ask questions about the Youtube video lecture")

# Input for YouTube video URL
video_url = st.text_input("Enter YouTube video URL")

# Button to fetch transcript
if st.button("Fetch Transcript"):
    if video_url:
        # Get video title first
        video_title = get_video_title(video_url)
        # st.subheader(f"Video: {video_title}")

        transcript = get_video_transcript(video_url)
        if transcript:
            # Save transcript to file and session state
            save_transcript_to_file(transcript)
            st.session_state.transcript = transcript
            st.session_state.video_title = video_title
            st.success("Transcript fetched successfully!")
            # Load transcript from file and split into chunks for processing
            loader = TextLoader(file_path="transcript.txt", encoding="utf-8")
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100, separators=["\n"]
            )
            texts = splitter.split_documents(documents)
            st.session_state.texts = texts
            # Clear any previous question when new transcript is loaded
            if "user_question" in st.session_state:
                del st.session_state.user_question
            st.success("Transcript processed successfully!")
        else:
            st.error("Failed to fetch transcript.")
    else:
        st.error("Please enter a valid YouTube video URL.")

# If transcript chunks are available, allow user to ask questions
if "texts" in st.session_state:
    # Display video title if available
    if "video_title" in st.session_state:
        st.subheader(f"Video: {st.session_state.video_title}")
    user_question = st.text_input("Ask a question:", key="user_question")
    if user_question:
        model_name = "sentence-transformers/all-mpnet-base-v2"
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name, cache_folder=".cache/huggingface"
        )
        # Create a FAISS vector store from transcript chunks
        vector_store = FAISS.from_documents(st.session_state.texts, embeddings)
        # Search for relevant transcript chunks based on user question
        match = vector_store.similarity_search(user_question)
        if match:
            # Set up LLM for answering questions
            llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.0, max_retries=2)
            chain = load_qa_chain(llm=llm, chain_type="stuff")
            response = chain.run(input_documents=match, question=user_question)
            st.subheader("Answer:")
            st.write(response)
        else:
            st.write("No relevant documents found for the question.")
