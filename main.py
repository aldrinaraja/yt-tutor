import os
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
        transcript = get_video_transcript(video_url)
        if transcript:
            # Save transcript to file and session state
            save_transcript_to_file(transcript)
            st.session_state.transcript = transcript
            st.success("Transcript fetched and saved successfully!")
            # Load transcript from file and split into chunks for processing
            loader = TextLoader(file_path="transcript.txt", encoding="utf-8")
            documents = loader.load()
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=100, separators=["\n"]
            )
            texts = splitter.split_documents(documents)
            st.session_state.texts = texts
            st.success("Transcript processed successfully!")
        else:
            st.error("Failed to fetch transcript.")
    else:
        st.error("Please enter a valid YouTube video URL.")

# If transcript chunks are available, allow user to ask questions
if "texts" in st.session_state:
    user_question = st.text_input("Ask a question:")
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
