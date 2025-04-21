import speech_recognition as sr
import pyttsx3

# Initialize the TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speaking speed

def text_to_speech(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    """Listen for a voice command and return it as text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"User said: {command}")
        return command
    except sr.UnknownValueError:
        text_to_speech("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        text_to_speech("Sorry, I am having trouble connecting to the speech service.")
        return ""
