import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import time
from scipy.io.wavfile import write
import speech_recognition as sr
import keyboard


def find_microphone_device_index():
    #Bu örnek, varsayılan mikrofonu döndürür. Gerekirse cihaz listesi bastırılabilir.
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        if "mic" in name.lower() or "input" in name.lower():
            print(f"Mikrofon bulundu: {name} (index {index})")
            return index
    print("Varsayılan mikrofon kullanılacak.")
    return None  #None => default mikrofon kullanılır

def sound_record_advanced(output_file, status_server=None):
    device_idx = find_microphone_device_index()

    r = sr.Recognizer()
    r.pause_threshold = 2

    try:
        with sr.Microphone(device_index=device_idx) as source:
            print("\nOrtam gürültüsü ayarlanıyor, lütfen bir saniye sessiz olun...")
            r.adjust_for_ambient_noise(source, duration=1)

            print("Hazır! Lütfen konuşmaya başlayın.")
            if status_server:
                status_server.update_vehicle_state("listening")
            
            audio = r.listen(source)

        print("Kayıt durdu. Ses dosyası kaydediliyor ve işleniyor...")

        #WAV dosyasını kaydet
        with open(output_file, "wb") as f:
            f.write(audio.get_wav_data())

        print(f"Ses başarıyla '{output_file}' olarak kaydedildi.")

        #Ses tanıma
        try:
            text = r.recognize_google(audio, language="tr-TR")
            if status_server and text:
                status_server.log_speech_output(text)
            return text
        except sr.UnknownValueError:
            print("Google Speech sesinizi anlayamadı.")
            return None
        except sr.RequestError as e:
            print(f"Google Speech servisine erişilemedi: {e}")
            return None

    except AssertionError as ae:
        print("Mikrofon düzgün başlatılamadı. Hata:", ae)
        return None
    except Exception as e:
        print("Beklenmeyen bir hata oluştu:", e)
        return None

def sound_record(output_file):
    """Record audio with automatic silence detection"""
    block_duration = 2  #saniye
    silence_threshold = 0.3  #ses seviyesi eşiği
    silence_duration = 1  #saniye: bu kadar süre sessizlik varsa kayıt biter

    #Set audio device and sample rate - try to find USB audio device
    samplerate = 44100  #Default sample rate
    try:
        devices = sd.query_devices()
        usb_device = None
        for i, device in enumerate(devices):
            if 'USB' in device['name'] and device['max_input_channels'] > 0:
                usb_device = i
                break
        
        if usb_device is not None:
            sd.default.device = usb_device
            device_info = devices[usb_device]
            samplerate = int(device_info['default_samplerate'])
            print(f"Using audio device: {device_info['name']}")
            print(f"Sample rate: {samplerate} Hz")
        else:
            print("No USB audio device found, using default")
            samplerate = 16000  #Fall back to 16kHz for default device
    except Exception as e:
        print(f"Audio device setup warning: {e}")
        samplerate = 44100  #Safe fallback

    print("Kayıt başlatılıyor... Konuşmaya başlayın.")

    recorded = []  #kaydedilen veriler
    silence_counter = 0
    start_time = time.time()

    try:
        while True:
            block = sd.rec(int(samplerate * block_duration), samplerate=samplerate, channels=1, dtype='float32')
            sd.wait()
            
            volume_norm = np.linalg.norm(block)  #ses seviyesi
            #print("Ses seviyesi:", volume_norm)

            if volume_norm > silence_threshold:
                recorded.append(block)
                silence_counter = 0  #yeniden sıfırla çünkü konuşma var
            else:
                if recorded:
                    silence_counter += block_duration
                    if silence_counter >= silence_duration:
                        print("Sessizlik tespit edildi. Kayıt durduruluyor.")
                        break

    except KeyboardInterrupt:
        print("Kullanıcı tarafından durduruldu.")

    #Veriyi birleştir ve WAV'e yaz
    if recorded:
        audio_data = np.concatenate(recorded, axis=0)
        wav.write(output_file, samplerate, (audio_data * 32767).astype(np.int16))
        print("Kayıt kaydedildi.")
    else:
        print("Hiç ses kaydedilmedi.")


def sound_record_manual(kayit_adi='kayit.wav', fs=16000):
    """
    Manual recording with 's' to start and 'e' to stop
    """
    #Set audio device - try to find USB audio device
    try:
        devices = sd.query_devices()
        usb_device = None
        for i, device in enumerate(devices):
            if 'USB' in device['name'] and device['max_input_channels'] > 0:
                usb_device = i
                break
        
        if usb_device is not None:
            sd.default.device = usb_device
            print(f"Using audio device: {devices[usb_device]['name']}")
    except Exception as e:
        print(f"Audio device setup warning: {e}")
        
    print("Başlamak için 's' tuşuna basın, bitirmek için 'e' tuşuna basın.")

    #Başlangıç tuşunu bekle
    keyboard.wait('s')
    print("Kayıt başladı...")

    kayitlar = []
    kayit_basliyor = True

    def callback(indata, frames, time, status):
        if kayit_basliyor:
            kayitlar.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        keyboard.wait('e')  #Bitirme tuşunu bekle
        print("Kayıt durduruldu.")

    #Veriyi birleştir
    ses_verisi = np.concatenate(kayitlar, axis=0)

    #float32'den int16'ya dönüştür (ses seviyesi için)
    ses_verisi = (ses_verisi * 32767).astype(np.int16)

    #Dosyaya yaz
    write(kayit_adi, fs, ses_verisi)
    print(f"Kayıt '{kayit_adi}' olarak kaydedildi.")
