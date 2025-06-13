import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
from preprocess import preprocess_text

# Загрузка данных
data = pd.read_csv("../data/train.csv")

# Предобработка текста
data['processed'] = data['question'].apply(preprocess_text)

# Разделение на тренировочную и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(data['processed'], data['label'], test_size=0.2, random_state=42)

# Создание и обучение векторизатора
vectorizer = TfidfVectorizer()
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Обучение модели
classifier = LogisticRegression(max_iter=1000)
classifier.fit(X_train_vec, y_train)

# Оценка модели
y_pred = classifier.predict(X_test_vec)
print(classification_report(y_test, y_pred))

# Создание папки models, если её нет
os.makedirs("../models", exist_ok=True)

# Сохранение модели и векторизатора
joblib.dump(classifier, "../models/nlp_classifier.joblib")
joblib.dump(vectorizer, "../models/vectorizer.joblib")
