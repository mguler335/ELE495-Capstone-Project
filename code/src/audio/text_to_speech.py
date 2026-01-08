import json
from google.cloud import texttospeech
from google.oauth2 import service_account


def text_to_speech(text, output_file, json_key_path):
    """Convert text to speech using Google Cloud Text-to-Speech API"""
    #Load service account JSON file
    with open(json_key_path) as f:
        info = json.load(f)
    credentials = service_account.Credentials.from_service_account_info(info)
    client = texttospeech.TextToSpeechClient(credentials=credentials)

    #Configure the text input
    synthesis_input = texttospeech.SynthesisInput(text=text)

    #Voice configuration (Turkish male voice)
    voice = texttospeech.VoiceSelectionParams(
        language_code="tr-TR",
        name="tr-TR-Chirp3-HD-Algieba",  #or "tr-TR-Standard-B"
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )

    #Audio file format configuration (MP3)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    #Send the request
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    #Save as MP3
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print("Audio file saved successfully")


text_to_speech('Kişi Kayıtlı Değil', '/home/bitirme/Desktop/ELE-495-Grup-8/data/kayitli.mp3', '/home/bitirme/Desktop/ELE-495-Grup-8/config/google_credentials.json')