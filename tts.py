from gtts import gTTS
import uuid
import os

def text_to_speech(text):
    filename = f"penguin_{uuid.uuid4()}.mp3"
    tts = gTTS(text, lang="en")
    tts.save(filename)
    return filename