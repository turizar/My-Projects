# 🎤 Complete Voice - Text Agent

A powerful multilingual voice agent application that provides seamless **Text-to-Speech** and **Speech-to-Text** functionality with automatic language detection for Spanish and English.

## ✨ Features

### 📝 Text-to-Speech (TTS)
- **Multilingual Support**: Automatically detects and converts text in Spanish and English
- **High-Quality Audio**: Uses Tacotron2-DDC models for natural-sounding speech
- **Speed Control**: Adjustable speech rate (0.5x to 2.0x)
- **Automatic Language Detection**: Smart detection based on text content

### 🎤 Speech-to-Text (STT)
- **Multiple Recording Options**:
  - Quick recording (5, 10, 15, 30 seconds)
  - Custom duration recording (1-60 seconds)
  - Manual start/stop recording
  - Audio file upload support
- **Google Speech Recognition**: High-accuracy transcription
- **Multilingual Recognition**: Supports Spanish and English audio
- **Real-time Processing**: Immediate transcription results

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- macOS (for full audio functionality)
- Internet connection (for Google Speech Recognition)

### Installation

1. **Clone or download the project**
```bash
cd Agente_Voz_Pro
```

2. **Create and activate virtual environment**
```bash
python -m venv voice_agent_env
source voice_agent_env/bin/activate  # On macOS/Linux
# or
voice_agent_env\Scripts\activate     # On Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install audio dependencies (macOS)**
```bash
# Install portaudio (required for PyAudio)
brew install portaudio

# Install additional audio libraries
pip install SpeechRecognition pyaudio
```

### Running the Application

```bash
streamlit run voice_text_agent.py
```

The application will be available at: **http://localhost:8501**

## 📖 How to Use

### Text-to-Speech
1. Navigate to the **"📝 Text to Speech"** tab
2. Enter your text in the text area
3. Adjust the speed slider if desired
4. Click **"🎵 Generate Audio"**
5. The system will:
   - Automatically detect the language (Spanish/English)
   - Generate high-quality audio
   - Display the audio player

### Speech-to-Text
1. Navigate to the **"🎤 Speech to Text"** tab
2. Choose your recording method:
   - **Quick Recording**: Click 5, 10, 15, or 30-second buttons
   - **Custom Recording**: Set duration with slider and click record
   - **Manual Recording**: Click "Start Recording" → speak → "Stop Recording"
   - **File Upload**: Upload an audio file (WAV, MP3, M4A, OGG)
3. Click **"🔄 Transcribe Audio"** to convert speech to text
4. Review the transcribed text in the results area

## 🛠️ Technical Details

### Models Used
- **TTS Models**:
  - English: `tts_models/en/ljspeech/tacotron2-DDC`
  - Spanish: `tts_models/es/mai/tacotron2-DDC` (with fallback to `tts_models/es/css10/vits`)
- **STT Engine**: Google Speech Recognition API

### Audio Specifications
- **Sample Rate**: 44,100 Hz
- **Format**: 16-bit PCM
- **Channels**: Mono
- **Output**: WAV format

### Language Detection
The application uses a word-frequency algorithm to automatically detect whether input text is in Spanish or English, ensuring optimal TTS model selection.

## 📋 Requirements

```
torch>=2.0.0
streamlit>=1.28.0
soundfile>=0.12.0
numpy>=1.21.0
TTS>=0.22.0
SpeechRecognition>=3.10.0
pyaudio>=0.2.11
```

## 🔧 Troubleshooting

### Common Issues

**"Audio recorder not available"**
- Install portaudio: `brew install portaudio`
- Reinstall PyAudio: `pip uninstall pyaudio && pip install pyaudio`

**"Could not load TTS models"**
- Ensure stable internet connection for model download
- Check available disk space (models are ~500MB each)

**"Recognition service error"**
- Verify internet connection
- Check Google Speech Recognition service status

**Recording issues on first use**
- This is a known issue with the manual recording feature
- Refresh the page after the first recording attempt
- Subsequent recordings will work normally

## 🌟 Tips for Best Results

### Text-to-Speech
- Use clear, well-structured text
- Avoid special characters or symbols
- Use punctuation for natural pauses
- Keep text length reasonable for faster processing

### Speech-to-Text
- Speak clearly and at moderate pace
- Minimize background noise
- Keep microphone close to your mouth
- Use short phrases for better accuracy
- Record in a quiet environment

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

---

**Made with ❤️ for seamless voice interaction**
