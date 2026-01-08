import os
import librosa
import numpy as np
import soundfile as sf

def add_noise(data, noise_level=0.005):
    noise = np.random.randn(len(data))
    return data + noise_level * noise

def time_shift(data, shift_max=0.2, sr=16000):
    shift = np.random.randint(-int(sr * shift_max), int(sr * shift_max))
    return np.roll(data, shift)

def time_stretch_librosa(data, rate=1.1):
    try:
        return librosa.effects.time_stretch(data, rate)
    except Exception as e:
        print(f"Time stretch hatası (rate={rate}): {e}")
        return data 

def pitch_shift_librosa(data, sr, n_steps=2):
    try:
        return librosa.effects.pitch_shift(data, sr, n_steps)
    except Exception as e:
        print(f"Pitch shift hatası (n_steps={n_steps}): {e}")
        return data 

def augment_audio(file_path):
    y, sr = librosa.load(file_path, sr=16000)
    augmented = []

    augmented.append(y)  
    augmented.append(add_noise(y))
    augmented.append(time_shift(y, sr=sr))
    augmented.append(time_stretch_librosa(y, rate=0.9))
    augmented.append(time_stretch_librosa(y, rate=1.1))
    augmented.append(pitch_shift_librosa(y, sr, n_steps=2))
    augmented.append(pitch_shift_librosa(y, sr, n_steps=-2))

    return augmented, sr

def process_folder(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".wav"):
            file_path = os.path.join(input_folder, filename)
            augmented_audios, sr = augment_audio(file_path)

            base_name = os.path.splitext(filename)[0]
            for i, aug in enumerate(augmented_audios):
                output_file = os.path.join(output_folder, f"{base_name}_aug_{i}.wav")
                sf.write(output_file, aug, sr)
                print(f"Saved: {output_file}")


