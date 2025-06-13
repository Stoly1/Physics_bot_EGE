import json
import os

# Загрузка базы заданий из JSON файла
def load_tasks(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Получение задания по теме и уровню пользователя
def get_task_for_user(topic, user_profile, tasks_db):
    level = user_profile.get(topic, "easy")
    tasks = tasks_db.get(topic)
    if not tasks:
        return "Задания по данной теме отсутствуют."
    return tasks.get(level, "Задания нужного уровня отсутствуют.")

# Обновление уровня пользователя после решения задания
def update_user_level(topic, success, user_profile):
    levels = ["easy", "medium", "hard"]
    current_level = user_profile.get(topic, "easy")
    idx = levels.index(current_level)
    if success and idx < len(levels) - 1:
        user_profile[topic] = levels[idx + 1]
    elif not success and idx > 0:
        user_profile[topic] = levels[idx - 1]
    return user_profile

def main():
    # Пути к файлам
    tasks_path = os.path.join(os.path.dirname(__file__), '../data/tasks.json')

    # Загрузка заданий
    tasks_db = load_tasks(tasks_path)

    # Пример профиля пользователя (в реальности можно загрузить из файла или базы)
    user_profile = {
        "work": "medium",
        "energy_conservation": "easy"
    }

    while True:
        topic = input("Введите тему задания (или 'exit' для выхода): ").strip()
        if topic == 'exit':
            break

        if topic not in tasks_db:
            print("Тема не найдена в базе заданий.")
            continue

        task = get_task_for_user(topic, user_profile, tasks_db)
        print(f"\nВаше задание ({user_profile.get(topic)} уровень):\n{task}")

        answer = input("\nРешили задание успешно? (да/нет): ").strip().lower()
        success = answer == 'да'
        user_profile = update_user_level(topic, success, user_profile)
        print(f"Обновленный профиль пользователя: {user_profile}\n")

if __name__ == "__main__":
    main()