import streamlit as st
import torch
from TTS.api import TTS
import tempfile
import os
import time
import base64
import io
import threading
import numpy as np
import soundfile as sf

# Try to import audio libraries
try:
    import speech_recognition as sr
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    st.warning("⚠️ For full audio functionality, install: pip install SpeechRecognition pyaudio")

# Use PyAudio for manual recording
RECORDER_AVAILABLE = True

# Page configuration
st.set_page_config(
    page_title="Complete Voice - Text Agent",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Complete Voice - Text Agent")
st.markdown("---")

# Function to initialize session variables
def initialize_session_state():
    """Initialize necessary session variables"""
    if 'recording_active' not in st.session_state:
        st.session_state.recording_active = False
    if 'recording_frames' not in st.session_state:
        st.session_state.recording_frames = []
    if 'recording_stream' not in st.session_state:
        st.session_state.recording_stream = None
    if 'recording_p' not in st.session_state:
        st.session_state.recording_p = None
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    if 'recognized_text' not in st.session_state:
        st.session_state.recognized_text = ""

# Initialize session variables
initialize_session_state()

# Function to detect language
def detect_language(text):
    """Detects if the text is in Spanish or English"""
    # Common Spanish words
    spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'me', 'ya', 'todo', 'esta', 'muy', 'sin', 'sobre', 'también', 'después', 'vida', 'años', 'año', 'vez', 'hacer', 'cada', 'donde', 'quien', 'durante', 'mientras', 'entre', 'hasta', 'desde', 'hacia', 'bajo', 'sobre', 'contra', 'según', 'mediante', 'excepto', 'salvo', 'menos', 'más', 'tanto', 'cuanto', 'cuando', 'donde', 'como', 'porque', 'aunque', 'si', 'que', 'quien', 'cual', 'cuyo', 'cuya', 'cuyos', 'cuyas']
    
    # Common English words
    english_words = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us']
    
    # Convert text to lowercase and split into words
    words = text.lower().split()
    
    # Count Spanish and English words
    spanish_count = sum(1 for word in words if word in spanish_words)
    english_count = sum(1 for word in words if word in english_words)
    
    # Determine language based on count
    if spanish_count > english_count:
        return 'es'
    elif english_count > spanish_count:
        return 'en'
    else:
        # If tied, use Spanish as default
        return 'es'

# Initialize multilingual TTS
@st.cache_resource
def load_multilingual_tts():
    """Load TTS models for Spanish and English"""
    models = {}
    
    try:
        # Model for English
        models['en'] = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
        st.success("✅ English TTS model loaded")
    except Exception as e:
        models['en'] = None
    
    try:
        # Model for Spanish
        models['es'] = TTS(model_name="tts_models/es/mai/tacotron2-DDC")
        st.success("✅ Spanish TTS model loaded")
    except Exception as e:
        try:
            # Fallback to alternative Spanish model
            models['es'] = TTS(model_name="tts_models/es/css10/vits")
            st.success("✅ Alternative Spanish TTS model loaded")
        except Exception as e2:
            models['es'] = models['en']  # Use English model as fallback
    
    return models

# Function to record audio with specific duration
def record_audio_simple(duration_seconds=5):
    """Records audio for a specific duration"""
    if not AUDIO_AVAILABLE:
        return None
    
    try:
        # Audio configuration
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        # Initialize pyaudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        frames = []
        
        # Record for the specified duration
        for i in range(0, int(RATE / CHUNK * duration_seconds)):
            data = stream.read(CHUNK)
            frames.append(data)
        
        # Stop and close stream
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Create WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            # Read file as bytes
            with open(tmp_file.name, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            return audio_bytes
            
    except Exception as e:
        st.error(f"Error recording audio: {e}")
        return None

def start_manual_recording():
    """Starts manual recording"""
    if not AUDIO_AVAILABLE:
        return False
    
    try:
        # Audio configuration
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        # Initialize pyaudio
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        # Save to session state
        st.session_state.recording_p = p
        st.session_state.recording_stream = stream
        st.session_state.recording_frames = []
        st.session_state.recording_active = True
        
        return True
        
    except Exception as e:
        st.error(f"Error starting recording: {e}")
        return False

def stop_manual_recording():
    """Stops manual recording and returns the audio"""
    if not st.session_state.recording_active:
        return None
    
    try:
        # Stop and close stream
        if st.session_state.recording_stream:
            st.session_state.recording_stream.stop_stream()
            st.session_state.recording_stream.close()
        
        if st.session_state.recording_p:
            st.session_state.recording_p.terminate()
        
        # Create WAV file
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            wf = wave.open(tmp_file.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(st.session_state.recording_frames))
            wf.close()
            
            # Read file as bytes
            with open(tmp_file.name, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Clear session state
            st.session_state.recording_active = False
            st.session_state.recording_frames = []
            st.session_state.recording_stream = None
            st.session_state.recording_p = None
            
            return audio_bytes
            
    except Exception as e:
        st.error(f"Error stopping recording: {e}")
        return None

def record_continuously():
    """Function to record continuously in background"""
    if st.session_state.recording_active and st.session_state.recording_stream:
        try:
            CHUNK = 1024
            # Read multiple chunks to ensure we capture audio
            for _ in range(10):  # Read 10 chunks at a time
                if st.session_state.recording_active:
                    data = st.session_state.recording_stream.read(CHUNK, exception_on_overflow=False)
                    st.session_state.recording_frames.append(data)
                else:
                    break
        except Exception as e:
            st.error(f"Error in continuous recording: {e}")
            st.session_state.recording_active = False

# Function to transcribe audio
def transcribe_audio(audio_bytes):
    """Transcribe audio using SpeechRecognition"""
    if not AUDIO_AVAILABLE:
        return "Error: SpeechRecognition is not available. Install: pip install SpeechRecognition pyaudio"
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file_path = tmp_file.name
        
        # Initialize recognizer
        r = sr.Recognizer()
        
        # Configure recognizer for better accuracy
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        r.operation_timeout = None
        r.phrase_threshold = 0.3
        r.non_speaking_duration = 0.8
        
        # Load and process audio
        with sr.AudioFile(tmp_file_path) as source:
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            # Record the audio
            audio_data = r.record(source)
        
        # Transcribe with multiple attempts
        text = None
        try:
            # Try with Spanish first
            text = r.recognize_google(audio_data, language='es-ES')
        except sr.UnknownValueError:
            try:
                # If it fails, try with English
                text = r.recognize_google(audio_data, language='en-US')
            except sr.UnknownValueError:
                try:
                    # If it fails, try without specifying language
                    text = r.recognize_google(audio_data)
                except sr.UnknownValueError:
                    return "Could not understand the audio. Try speaking more clearly and with less background noise."
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        if text:
            return text
        else:
            return "Could not transcribe the audio. Check that the microphone is working correctly."
        
    except sr.RequestError as e:
        return f"Recognition service error: {e}. Check your internet connection."
    except Exception as e:
        return f"Error processing audio: {e}"

# Load multilingual TTS models
with st.spinner("Loading TTS models..."):
    tts_models = load_multilingual_tts()

if not tts_models or (tts_models.get('en') is None and tts_models.get('es') is None):
    st.error("Could not load TTS models")
    st.stop()

# Create tabs
tab1, tab2 = st.tabs(["📝 Text to Speech", "🎤 Speech to Text"])

with tab1:
    st.subheader("📝 Convert Text to Audio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        text = st.text_area(
            "Write your text here:",
            height=200,
            placeholder="Write here the text you want to convert to audio..."
        )
        
        # Simple controls
        speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
        
        # Generation button
        if st.button("🎵 Generate Audio", type="primary"):
            if text.strip():
                with st.spinner("Generating audio..."):
                    try:
                        # Detect text language
                        detected_language = detect_language(text)
                        language_name = "Spanish" if detected_language == 'es' else "English"
                        
                        # Show detected language
                        st.info(f"🌍 **Detected language:** {language_name}")
                        
                        # Load TTS models
                        tts_models = load_multilingual_tts()
                        tts_model = tts_models.get(detected_language)
                        
                        if tts_model is None:
                            st.error(f"❌ Could not load TTS model for {language_name}")
                        else:
                            # Create temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                                tmp_file_path = tmp_file.name
                            
                            # Generate audio using the appropriate model
                            tts_model.tts_to_file(
                                text=text,
                                file_path=tmp_file_path,
                                speed=speed
                            )
                            
                            # Verify that the file was created correctly
                            if os.path.exists(tmp_file_path) and os.path.getsize(tmp_file_path) > 0:
                                # Show audio
                                st.success(f"✅ Audio generated successfully in {language_name}!")
                                st.audio(tmp_file_path, format="audio/wav")
                                
                                # Show file information
                                file_size = os.path.getsize(tmp_file_path)
                                st.info(f"📁 File size: {file_size:,} bytes")
                                
                                # Clean up temporary file
                                os.unlink(tmp_file_path)
                            else:
                                st.error("❌ Error: Could not generate audio file")
                            
                    except Exception as e:
                        st.error(f"Error generating audio: {e}")
                        # Clean up temporary file in case of error
                        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                            os.unlink(tmp_file_path)
            else:
                st.warning("Please write some text")
    
    with col2:
        st.subheader("ℹ️ TTS Information")
        st.info("**Models:** Tacotron2-DDC (ES/EN)")
        st.info("**Languages:** Spanish and English")
        st.info("**Detection:** Automatic")
        st.info("**Quality:** High")
        st.info("**Speed:** Fast")
        
        st.subheader("🎛️ Controls")
        st.markdown("- **Speed**: Controls how fast it speaks")
        st.markdown("- **Text**: The content to convert")
        st.markdown("- **Audio**: Generated automatically")
        
        st.subheader("💡 Tips")
        st.markdown("- Write clear and well-structured text")
        st.markdown("- **Spanish and English** detected automatically")
        st.markdown("- Avoid special characters or symbols")
        st.markdown("- Use punctuation for natural pauses")
        st.markdown("- Long texts may take longer to process")
        st.markdown("- Language mixing may cause confusion")

with tab2:
    st.subheader("🎤 Convert Speech to Text")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("ℹ️ STT Information")
        if AUDIO_AVAILABLE:
            st.success("**Status:** ✅ Functional")
            st.info("**Engine:** Google Speech Recognition")
            st.info("**Language:** Spanish")
            st.info("**Quality:** High")
        else:
            st.warning("**Status:** ⚠️ Limited")
            st.info("**Engine:** Not available")
            st.info("**Language:** N/A")
            st.info("**Quality:** N/A")
        
        st.subheader("🎛️ Instructions")
        st.markdown("1. **Select** duration (5, 10, 15, 30 sec)")
        st.markdown("2. **Click** the record button")
        st.markdown("3. **Speak** clearly")
        st.markdown("4. **Transcribe** the audio")
        st.markdown("5. **Review** the text")
        
        st.subheader("💡 Tips")
        st.markdown("- Speak clearly and slowly")
        st.markdown("- Avoid background noise")
        st.markdown("- Keep microphone close")
        st.markdown("- Use short phrases")
        st.markdown("- Record in a quiet environment")
        st.markdown("- Maximum 10 minutes of recording")
        
        st.subheader("🔧 Installation")
        st.markdown("For full functionality:")
        st.code("""
# Install portaudio (macOS only)
brew install portaudio

# Install Python dependencies
pip install SpeechRecognition pyaudio
        """)
    
    with col2:
        st.markdown("### 🎙️ Audio Recording")
        
        # Session state
        if 'recognized_text' not in st.session_state:
            st.session_state.recognized_text = ""
        if 'recorded_audio' not in st.session_state:
            st.session_state.recorded_audio = None
        if 'recording' not in st.session_state:
            st.session_state.recording = False
        if 'audio_data' not in st.session_state:
            st.session_state.audio_data = None
        
        # Check recording availability
        if RECORDER_AVAILABLE and AUDIO_AVAILABLE:
            st.success("✅ Audio recorder available")
            
            # Recording with predefined durations
            st.markdown("### 🎤 Quick Recording")
            st.info("Select duration and click record. Recording will stop automatically.")
            
            # Quick duration buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🎤 5 sec", type="primary"):
                    with st.spinner("Recording 5 seconds..."):
                        st.warning("🔴 **RECORDING...** Speak now!")
                        audio_bytes = record_audio_simple(5)
                        if audio_bytes:
                            st.session_state.audio_data = audio_bytes
                            st.success("✅ Recording completed!")
                        else:
                            st.error("❌ Recording error")
            
            with col2:
                if st.button("🎤 10 sec"):
                    with st.spinner("Recording 10 seconds..."):
                        st.warning("🔴 **RECORDING...** Speak now!")
                        audio_bytes = record_audio_simple(10)
                        if audio_bytes:
                            st.session_state.audio_data = audio_bytes
                            st.success("✅ Recording completed!")
                        else:
                            st.error("❌ Recording error")
            
            with col3:
                if st.button("🎤 15 sec"):
                    with st.spinner("Recording 15 seconds..."):
                        st.warning("🔴 **RECORDING...** Speak now!")
                        audio_bytes = record_audio_simple(15)
                        if audio_bytes:
                            st.session_state.audio_data = audio_bytes
                            st.success("✅ Recording completed!")
                        else:
                            st.error("❌ Recording error")
            
            with col4:
                if st.button("🎤 30 sec"):
                    with st.spinner("Recording 30 seconds..."):
                        st.warning("🔴 **RECORDING...** Speak now!")
                        audio_bytes = record_audio_simple(30)
                        if audio_bytes:
                            st.session_state.audio_data = audio_bytes
                            st.success("✅ Recording completed!")
                        else:
                            st.error("❌ Recording error")
            
            # Custom recording
            st.markdown("### 🎛️ Custom Recording")
            custom_duration = st.slider("Custom duration (seconds)", 1, 60, 10)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🎤 Record {custom_duration} sec", type="secondary"):
                    with st.spinner(f"Recording {custom_duration} seconds..."):
                        st.warning("🔴 **RECORDING...** Speak now!")
                        audio_bytes = record_audio_simple(custom_duration)
                        if audio_bytes:
                            st.session_state.audio_data = audio_bytes
                            st.success("✅ Recording completed!")
                        else:
                            st.error("❌ Recording error")
            
            with col2:
                if st.button("🗑️ Clear All"):
                    st.session_state.audio_data = None
                    st.session_state.recorded_audio = None
                    st.session_state.recognized_text = ""
            
            # Manual recording (true)
            st.markdown("### 🎤 Manual Recording (Start/Stop)")
            st.info("Manual recording: press 'Start' to begin and 'Stop' to finish.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔴 Start Recording", type="primary", disabled=st.session_state.recording_active):
                    if start_manual_recording():
                        st.success("✅ Recording started! Speak now...")
                        st.session_state.recording_started = True
                    else:
                        st.error("❌ Error starting recording")
            
            with col2:
                if st.button("⏹️ Stop Recording", type="secondary", disabled=not st.session_state.recording_active):
                    audio_bytes = stop_manual_recording()
                    if audio_bytes:
                        st.session_state.audio_data = audio_bytes
                        st.success("✅ Recording stopped and saved!")
                    else:
                        st.error("❌ Error stopping recording")
            
            # Show recording status
            if st.session_state.recording_active:
                st.warning("🔴 **RECORDING...** Speak now! Press 'Stop' when finished.")
                
                # Record continuously without blocking the UI
                if st.session_state.recording_stream:
                    record_continuously()
                
                # Auto-refresh to continue recording
                time.sleep(0.1)
                st.rerun()
            
            # Show audio if available
            if st.session_state.audio_data:
                st.markdown("### 🎵 Recorded Audio")
                st.info("Audio recorded successfully. Click 'Transcribe Audio' to convert to text.")
                
                # Show the audio
                st.audio(st.session_state.audio_data, format="audio/wav")
                
                # Button to transcribe
                if st.button("🔄 Transcribe Audio", type="primary"):
                    with st.spinner("Transcribing audio..."):
                        transcribed_text = transcribe_audio(st.session_state.audio_data)
                        st.session_state.recognized_text = transcribed_text
                        if transcribed_text and not transcribed_text.startswith("Error"):
                            st.success("✅ Transcription completed!")
                        else:
                            st.error("❌ Transcription error")
        
        else:
            st.warning("⚠️ Recorder not available. Use the file upload option.")
            
            # Fallback: upload audio file
            st.markdown("### 📁 Upload Audio File")
            uploaded_file = st.file_uploader(
                "Upload an audio file (WAV, MP3, etc.)",
                type=['wav', 'mp3', 'm4a', 'ogg']
            )
            
            if uploaded_file:
                st.session_state.recorded_audio = uploaded_file.read()
                st.success("✅ File uploaded successfully!")
                
                # Show audio
                st.audio(uploaded_file, format="audio/wav")
                
                # Button to transcribe
                if st.button("🔄 Transcribe Audio", type="primary"):
                    with st.spinner("Transcribing audio..."):
                        transcribed_text = transcribe_audio(uploaded_file.read())
                        st.session_state.recognized_text = transcribed_text
                        st.success("✅ Transcription completed!")
        
        # Recognized text area
        st.markdown("### 📝 Recognized Text")
        recognized_text = st.text_area(
            "Transcribed text:",
            value=st.session_state.recognized_text,
            height=150,
            placeholder="The recognized text will appear here..."
        )
        
        # Show recognized text if it exists
        if st.session_state.recognized_text:
            st.markdown("---")
            st.markdown("### 📋 Result:")
            st.info(st.session_state.recognized_text)
    

# Footer
st.markdown("---")
st.markdown("*Complete Voice Agent - Text to Speech and Speech to Text*")
