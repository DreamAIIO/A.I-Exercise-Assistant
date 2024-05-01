import tempfile
import requests
import json
import streamlit as st
from api import *

st.title("AI Fitness Coach 🤸🤖")

uploaded_file = st.file_uploader("Upload a video 🎥", type=["mp4", "mov", "avi"])
if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    st.video(tfile.name)
    inputs = {"video": str(tfile.name)}
    # Notice how I call get_feedback() as soon as the video is uploaded and I don't wait for the user to click a button.
    # This gives a better user experience as the user doesn't have to wait as long for the feedback.
    with st.spinner("👀"):
        feedback = requests.post(url = "http://127.0.0.1:8000/messagesFeedback",
                            data = json.dumps(inputs))
        st.write(feedback.text)