# import whisper
# from pydub import AudioSegment
# import os
# import uuid

# model = whisper.load_model("base")  # You can use 'small' or 'medium' for better accuracy

# def transcribe_voice(ogg_path):
#     # Convert OGG to WAV
#     wav_path = f"temp_{uuid.uuid4()}.wav"
#     audio = AudioSegment.from_file(ogg_path)
#     audio.export(wav_path, format="wav")

#     # Transcribe with Whisper
#     result = model.transcribe(wav_path)
#     os.remove(wav_path)
#     return result["text"]
