import joblib
from preprocess import preprocess_text

# Загрузка модели и векторизатора
model = joblib.load("../models/nlp_classifier.joblib")  # логистическая регрессия
vectorizer = joblib.load("../models/vectorizer.joblib")  # TfidfVectorizer

def predict_topic(question, threshold=0.4):
    processed = preprocess_text(question)
    X = vectorizer.transform([processed])
    proba = model.predict_proba(X)[0]
    max_proba = max(proba)
    predicted_label = model.classes_[proba.argmax()]

    if max_proba < threshold:
        return None, max_proba
    else:
        return predicted_label, max_proba

if __name__ == "__main__":
    while True:
        user_input = input("Введите вопрос (или 'exit' для выхода): ")
        if user_input.lower() == 'exit':
            break
        topic, confidence = predict_topic(user_input)
        if topic is None:
            print("Тема не распознана.")
        else:
            print(f"Предсказанная тема: {topic} (уверенность {confidence:.2f})")