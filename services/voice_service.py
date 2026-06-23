import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from utils.helpers import clean_text_for_tts

def transcribe_audio(audio_bytes):
    """
    Transcribes audio bytes into text using SpeechRecognition and Google Web Speech API.
    Streamlit st.audio_input provides WAV or WEBM bytes. SpeechRecognition requires WAV,
    AIFF, or FLAC.
    """
    if not audio_bytes:
        return ""
    
    # Write to a temporary file
    temp_dir = tempfile.gettempdir()
    temp_filepath = os.path.join(temp_dir, "calmmind_input.wav")
    
    try:
        with open(temp_filepath, "wb") as f:
            f.write(audio_bytes)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_filepath) as source:
            # Adjust for ambient noise if needed
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Speech was unclear, please try speaking again or use text chat."
    except sr.RequestError as e:
        return f"Speech recognition service error: {e}"
    except Exception as e:
        # If SpeechRecognition fails (e.g. invalid WAV format), let the user know
        return f"Could not process audio: {str(e)}. Please type your message."
    finally:
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except:
                pass

def text_to_speech(text):
    """
    Converts text to speech using gTTS and returns the file path of the generated audio.
    Streamlit can read this file path to play back to the user.
    """
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_audio")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Clean text slightly (remove symbols or markdown formatting that sounds weird in speech)
    clean_text = clean_text_for_tts(text)
    
    # Save the output audio file
    filename = f"speech_{hash(clean_text) % 1000000}.mp3"
    filepath = os.path.join(temp_dir, filename)
    
    # Clean up old files in the directory to prevent cluttering
    try:
        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                # If file is older than 5 minutes, delete it
                if os.path.getmtime(file_path) < (os.time() if hasattr(os, 'time') else datetime.now().timestamp() if hasattr(datetime, 'now') else 0) - 300:
                    os.remove(file_path)
    except:
        pass
        
    try:
        tts = gTTS(text=clean_text[:500], lang='en', slow=False) # cap at 500 characters for speed
        tts.save(filepath)
        return filepath
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
