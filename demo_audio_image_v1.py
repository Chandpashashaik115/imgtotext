import streamlit as st
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
import os
from pydub import AudioSegment
import tempfile

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Function to process image input
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to setup image for processingcld
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to summarize audio
@st.cache_data(show_spinner=False)
def summarize_audio(audio_file_path, input_prompt):
    model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
    audio_file = genai.upload_file(path=audio_file_path)
    response = model.generate_content([input_prompt, audio_file])
    return response.text

# Function to save uploaded audio file
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.' + uploaded_file.name.split('.')[-1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None

# Initialize Streamlit app
st.set_page_config(page_title="Gemini Application")
st.header("Gemini Application")

# UI for Image Processing
st.subheader("Image Processing")
input_text_image = st.text_input("Input Prompt for Image:", key="input_image")
uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="upload_image")
if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image.", use_column_width=True)
submit_image = st.button("Submit Image")

# UI for Audio Processing
st.subheader("Audio Processing")
input_text_audio = st.text_input("Input Prompt for Audio:", key="input_audio")
audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3', 'm4a'], key="upload_audio")
if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)
    st.audio(audio_path)
submit_audio = st.button("Convert Audio into Text")

# Processing and Displaying Results
if submit_image:
    image_data = input_image_setup(uploaded_image)
    input_prompt_image = "You are an expert in understanding invoices. You will receive input images as invoices & you will have to answer questions based on the input image"
    response = get_gemini_response(input_prompt_image, image_data, input_text_image)
    st.subheader("Response from Image:")
    st.write(response)

if submit_audio:
    with st.spinner('Converting...'):
        input_prompt_audio = "Please summarize the following audio and convert the audio into text"
        summary_text = summarize_audio(audio_path, input_text_audio)
        st.subheader("Text from Audio:")
        st.info(summary_text)