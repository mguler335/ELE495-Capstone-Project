import io
import json
from pydub import AudioSegment
from google.cloud import speech
from google.oauth2 import service_account


def speech_to_text(sound_file, json_key_path, status_server=None):
    """Convert speech to text using Google Cloud Speech API"""
    #Load JSON credentials
    with open(json_key_path) as f:
        info = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(info)
    client = speech.SpeechClient(credentials=credentials)

    #Open with AudioSegment, convert to mono, then get as bytes
    sound = AudioSegment.from_wav(sound_file)
    sound = sound.set_channels(1)                #Convert to mono
    buf = io.BytesIO()
    sound.export(buf, format="wav")              #Write to buffer as WAV
    content = buf.getvalue()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="tr-TR"
    )
    
    response = client.recognize(config=config, audio=audio)
    
    for result in response.results:
        transcript = str(result.alternatives[0].transcript)
        confidence = result.alternatives[0].confidence
        
        if status_server:
            status_server.log_speech_output(transcript, confidence)
        
        return transcript
    
    return None