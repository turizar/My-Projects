import pyttsx3
import speech_recognition as sr
import pywhatkit
import yfinance as yf
import pyjokes
import webbrowser
import datetime
import wikipedia
import os
import pyaudio
import wave

# Add path virtual environment of FLAC to the PATH
flac_path = "C:\\Users\\tomas\\Downloads\\flac-1.3.2\\flac-1.3.2-win\\win64"
os.environ["PATH"] += os.pathsep + flac_path

# Voice / language options
id3 = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_HELENA_11.0"

# Function to make the assistant speak
def speak(message):
    engine = pyttsx3.init()
    engine.setProperty("voice", id3)
    engine.say(message)
    engine.runAndWait()

# Function to recognize speech
def recognize_speech():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        r.adjust_for_ambient_noise(source)
        print("You can speak now")
        try:
            audio_data = r.listen(source)
            print("Audio captured successfully")
            with wave.open("input.wav", "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(pyaudio.PyAudio().get_sample_size(pyaudio.paInt16))
                wav_file.setframerate(44100)
                wav_file.writeframes(audio_data.frame_data)
            return r.recognize_google(audio_data)
        except sr.UnknownValueError:
            print("Oops, I didn't understand")
            return "still waiting"
        except sr.RequestError as e:
            print("Oops, there's no service:", e)
            return "still waiting"
        except Exception as e:
            print("Unexpected error:", str(e))
            return "still waiting"

# Get the day of the week
def get_day():
    today = datetime.date.today()
    calendar = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"}
    speak(f"Today is {calendar[today.weekday()]}")

# Get the current time
def get_time():
    current_time = datetime.datetime.now()
    current_time = f"It's currently {current_time.hour} hours and {current_time.minute} minutes"
    speak(current_time)

# Initial greeting
def initial_greeting():
    current_time = datetime.datetime.now()
    if current_time.hour < 6 or current_time.hour > 20:
        greeting = "Good evening"
    elif 6 <= current_time.hour < 12:
        greeting = "Good morning"
    else:
        greeting = "Good afternoon"
    speak(f"{greeting}, I'm your personal assistant. How can I help you?")

# Main function of the assistant
def request_things():
    initial_greeting()
    while True:
        request = recognize_speech()
        print("Request:", request)  # Debugging message
        if "open youtube" in request:
            print("Opening YouTube")  # Debugging message
            speak("Opening YouTube")
            webbrowser.open("https://www.youtube.com")
        elif "open email" in request:
            print("Opening your email")  # Debugging message
            speak("Opening your email")
            webbrowser.open("https://www.gmail.com")
        elif "open browser" in request:
            print("Opening the browser")  # Debugging message
            speak("Opening the browser")
            webbrowser.open("https://www.google.com")
        elif "what day is it" in request:
            get_day()
        elif "what time is it" in request:
            get_time()
        elif "search on wikipedia" in request:
            speak("Searching on Wikipedia")
            request = request.replace("search on wikipedia", "")
            wikipedia.set_lang("en")
            result = wikipedia.summary(request, sentences=1)
            speak(result)
        elif "search on internet" in request:
            speak("Searching on the internet")
            request = request.replace("search on internet",  "")
            pywhatkit.search(request)
            speak("Here's what I found")
        elif "play" in request:
            speak("Playing on YouTube")
            pywhatkit.playonyt(request)
        elif "joke" in request:
            speak(pyjokes.get_joke())
        elif "stock price" in request:
            portfolio = {"apple": "AAPL", "amazon": "AMZN", "google": "GOOGL"}
            stock = request.split("of")[-1].strip()
            try:
                searched_stock = portfolio[stock]
                searched_stock = yf.Ticker(searched_stock)
                current_price = searched_stock.info["regularMarketPrice"]
                speak(f"The price of {stock} is {current_price}")
            except:
                speak("Sorry, I couldn't find it")
        elif "goodbye" in request or "exit program" in request:
            speak("Ok, I'm going to rest.")
            break
        else:
            speak("I'm sorry, I didn't catch that. Can you repeat?")

# Calling the main function
request_things()