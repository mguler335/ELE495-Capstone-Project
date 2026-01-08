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


def predict_multi_class(file_path, model_path="models/modelV3/multiclass_model.joblib", le_path="models/modelV3/label_encoder.joblib"):
    model = joblib.load(model_path)
    le = joblib.load(le_path)
    features = extract_featuresV2(file_path)
    features = features.reshape(1, -1)  
    pred_enc = model.predict(features)[0]
    pred_label = le.inverse_transform([pred_enc])[0]
    return pred_label


def predict_class(audio_path, model_path="models/multiclass_with_others_svm.pkl"):
    """Predict command class from audio"""
    #Modeli yükle
    if not os.path.exists(model_path):
        print(f"Model bulunamadı: {model_path}")
        return

    model = joblib.load(model_path)

    #Özellikleri çıkar
    features = extract_features(audio_path)
    if features is None:
        print("Özellik çıkarımı başarısız.")
        return

    #Yeniden şekillendir (tek örnek için)
    features = features.reshape(1, -1)

    #Tahmin
    predicted_class = model.predict(features)[0]
    predicted_probs = model.predict_proba(features)[0]

    print(f"Tahmin edilen sınıf: {predicted_class}")
    print("Sınıf olasılıkları:")
    for cls, prob in zip(model.classes_, predicted_probs):
        print(f"  {cls}: {prob:.3f}")
    
    return predicted_class