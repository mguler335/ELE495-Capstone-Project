import joblib
import os
import sys

#Add paths for flexible imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

try:
    #Try relative imports first (when running from src directory)
    from ml.feature_extraction import extract_features, extract_featuresV2
except ImportError:
    #Fallback to absolute imports (when running from project root)
    from src.ml.feature_extraction import extract_features, extract_featuresV2


def predict_one_class(file_path, model_path="models/modelV3/one_class_svm_model.joblib"):
    model = joblib.load(model_path)
    features = extract_featuresV2(file_path)
    features = features.reshape(1, -1) 
    pred = model.predict(features)
    return pred[0]


def predict_speaker(audio_path, model_path='models/oneclass_svm_speaker.pkl'):
    """Predict if audio belongs to the target speaker"""
    #Modeli yükle
    model = joblib.load(model_path)

    #Özellik çıkar
    features = extract_features(audio_path)
    if features is None:
        return "Ses dosyası işlenemedi."

    #Yeniden şekillendir, çünkü tek örnek var
    features = features.reshape(1, -1)

    #Tahmin et
    prediction = model.predict(features)

    if prediction[0] == 1:
        return f"🔊 Bu ses, hedef konuşmacıya AİT ✅"
    else:
        return f"🔕 Bu ses, hedef konuşmacıya AİT DEĞİL ❌"