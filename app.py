import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os
from dotenv import load_dotenv  
load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"] )
except KeyError:
    st.error("🚨 GOOGLE_API_KEY environment variable not set!")
    st.info("Please set your Google API key as an environment variable to use this app.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred during API configuration: {e}")
    st.stop()



def get_gemini_response(transcript_text, prompt):
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        if st.session_state.summary:
            st.markdown("---")
            st.subheader("Summary in Key Points:")
           
            st.markdown(st.session_state.summary)
           
            st.download_button(
                label="📥 Download Summary (.txt)",
                data=st.session_state.summary,
                file_name="youtube_summary.txt",
                mime="text/plain"
            )

        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"An error occurred while generating the summary: {e}")
        return None

def extract_transcript_details(youtube_video_url):
   
    try:
       
        if "youtu.be/" in youtube_video_url:
            video_id = youtube_video_url.split("youtu.be/")[1].split("?")[0]
        elif "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("v=")[1].split("&")[0]
        else:
            st.error("Invalid YouTube URL format.")
            return None
            
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

       
        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        st.error(f"An error occurred while fetching the transcript: {e}")
        st.warning("This might be due to an invalid URL, a private video, or a video without a transcript.")
        return None

st.set_page_config(page_title="YouTube Summarizer", page_icon="📝", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
        text-align: center;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 30px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #007B9A;
    }
    .stDownloadButton>button {
        background-color: #008CBA;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 20px 2px 4px 2px;
        cursor: pointer;
        border-radius: 12px;
    }
    .stDownloadButton>button:hover {
        background-color: #007B9A;
    }
    .summary-box {
        background-color: #000;
        color: #fff;
        border-left: 5px solid #4CAF50;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)


if 'summary' not in st.session_state:
    st.session_state.summary = None

st.markdown('<p class="main-header">YouTube Video Summarizer</p>', unsafe_allow_html=True)
st.write("Enter the YouTube video link below to get a summary in key points.")

youtube_link = st.text_input("Enter YouTube Video Link:", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ")

#prompt
prompt = """
You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video in key points. Please provide the summary
as a list of important points.
The transcript text is: 
"""


if st.button("Get Summary"):
    if youtube_link:
        with st.spinner('Extracting transcript and generating summary...'):
            transcript_text = extract_transcript_details(youtube_link)

            if transcript_text:
                summary = get_gemini_response(transcript_text, prompt)
                if summary:
                    st.session_state.summary = summary # Store summary in session state
    else:
        st.warning("Please enter a YouTube video link.")

if st.session_state.summary:
    st.markdown("---")
    st.subheader("Summary in Key Points:")
    st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>', unsafe_allow_html=True)
    
    # Download button
    st.download_button(
        label="📥 Download Summary (.txt)",
        data=st.session_state.summary,
        file_name="youtube_summary.txt",
        mime="text/plain"
    )


st.markdown("---")
