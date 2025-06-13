import logging
import joblib
import json
import os
import datetime
import warnings
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters
)
from preprocess import preprocess_text

warnings.filterwarnings("ignore", category=UserWarning, module="apscheduler")

# Пути к моделям и базе заданий
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "../models/nlp_classifier.joblib")
vectorizer_path = os.path.join(base_dir, "../models/vectorizer.joblib")
tasks_path = os.path.join(base_dir, "../data/tasks.json")
feedback_log_path = os.path.join(base_dir, "../data/feedback_log.json")  # ✅ путь к файлу отзывов

# Загрузка модели и векторизатора
model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# Загрузка базы заданий
with open(tasks_path, "r", encoding="utf-8") as f:
    tasks_db = json.load(f)

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Хранилище состояния пользователей
user_state = {}

# Словарь ключевых слов для обратной связи
feedback_keywords = {
    "сложно": "too_hard",
    "непонятно": "unclear",
    "понятно": "clear",
    "ещё": "want_more",
    "не по теме": "off_topic"
}

# Функция предсказания темы
def predict_topic(question):
    processed = preprocess_text(question)
    X = vectorizer.transform([processed])
    prediction = model.predict(X)[0]
    return prediction

# Получение задания по теме и уровню сложности
def get_task(topic, difficulty):
    tasks = tasks_db.get(topic, {}).get(difficulty)
    if not tasks:
        return "Нет заданий по данной теме."
    return tasks[0] if isinstance(tasks, list) else tasks

# Сохранение отзыва пользователя
def save_feedback(user_id, text, label):
    feedback = {
        "user_id": user_id,
        "text": text,
        "label": label,
        "timestamp": datetime.datetime.now().isoformat()
    }

    if not os.path.exists(feedback_log_path):
        with open(feedback_log_path, "w", encoding="utf-8") as f:
            json.dump([feedback], f, ensure_ascii=False, indent=2)
    else:
        with open(feedback_log_path, "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
            data.append(feedback)
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)

# Основной обработчик сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text.lower()

    # Обработка ключевых слов обратной связи
    for keyword, label in feedback_keywords.items():
        if keyword in text:
            save_feedback(user_id, text, label)
            if label == "too_hard":
                await update.message.reply_text("Хорошо, попробуем задание попроще.")
            elif label == "unclear":
                await update.message.reply_text("Попробую объяснить по-другому.")
            elif label == "clear":
                await update.message.reply_text("Рад, что всё понятно!")
            elif label == "want_more":
                await update.message.reply_text("Вот ещё одно задание!")
            elif label == "off_topic":
                await update.message.reply_text("Попробую подобрать более подходящее.")
            return

    # Сброс состояния
    if text == "сброс":
        user_state.pop(user_id, None)
        await update.message.reply_text("Прогресс сброшен.")
        return

    # Новая сессия: определить тему
    if user_id not in user_state:
        topic = predict_topic(text)
        user_state[user_id] = {"topic": topic, "difficulty": "easy"}
        await update.message.reply_text(
            f"Определена тема: *{topic}*", parse_mode="Markdown"
        )

    # Подача задания
    topic = user_state[user_id]["topic"]
    difficulty = user_state[user_id]["difficulty"]
    task = get_task(topic, difficulty)

    await update.message.reply_text(
        f"Задание уровня *{difficulty}* по теме *{topic}*:\n\n{task}",
        parse_mode="Markdown"
    )

# Запуск бота
def main():
    TOKEN = "8026427980:AAFEgTvAM6VPWlrNK84s9vU-XJve7m1SzuY"  # ← вставь свой токен

    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()