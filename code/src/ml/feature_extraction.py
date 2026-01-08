import librosa
import numpy as np
import warnings
warnings.filterwarnings("ignore", message="n_fft=\\d+ is too large for input signal")
warnings.filterwarnings("ignore", message="Empty filters detected in mel frequency basis.*")


def extract_featuresV2(file_path, n_fft=128):
    y, sr = librosa.load(file_path, sr=16000)
    if len(y) < n_fft:
        y = np.pad(y, (0, n_fft - len(y)), mode='constant')
    
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, n_fft=n_fft)
    mfccs_mean = np.mean(mfccs, axis=1)
    mfccs_var = np.var(mfccs, axis=1)
    
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=n_fft)
    chroma_mean = np.mean(chroma, axis=1)
    chroma_var = np.var(chroma, axis=1)
    
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    mel_mean = np.mean(mel_db, axis=1)
    mel_var = np.var(mel_db, axis=1)
    
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr, n_fft=n_fft)
    contrast_mean = np.mean(contrast, axis=1)
    contrast_var = np.var(contrast, axis=1)
    
    y_harmonic = librosa.effects.harmonic(y)
    tonnetz = librosa.feature.tonnetz(y=y_harmonic, sr=sr)
    tonnetz_mean = np.mean(tonnetz, axis=1)
    tonnetz_var = np.var(tonnetz, axis=1)
    
    features = np.concatenate([
        mfccs_mean, mfccs_var,
        chroma_mean, chroma_var,
        mel_mean, mel_var,
        contrast_mean, contrast_var,
        tonnetz_mean, tonnetz_var
    ])
    
    return features

# Özellik çıkarımı (eğitimdeki ile aynı olmalı)
def extract_features(file_path, mfcc=True, chroma=True, mel=True):
    try:
        y, sr = librosa.load(file_path, sr=22050)
        if len(y) < 22050:
            y = np.pad(y, (0, 22050 - len(y)), 'constant')

        result = np.array([])

        if mfcc:
            mfccs = np.mean(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40).T, axis=0)
            result = np.hstack((result, mfccs))
        if chroma:
            chroma_feat = np.mean(librosa.feature.chroma_stft(y=y, sr=sr).T, axis=0)
            result = np.hstack((result, chroma_feat))
        if mel:
            mel_feat = np.mean(librosa.feature.melspectrogram(y=y, sr=sr).T, axis=0)
            result = np.hstack((result, mel_feat))
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None
    return result