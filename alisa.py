"""
Навык для PyCompanion: "Кто хочет стать миллионером"
Авторы: Ибрагим и Степа
Версия: 1.1
Все данные хранятся в коде. Базы данных не используются.
"""

import json
import random
import os
from datetime import datetime


# КОНФИГУРАЦИЯ И ДАННЫЕ


# Суммы выигрыша за каждый из 15 вопросов
PRIZE_LADDER = [
    100, 200, 300, 500, 1000,
    2000, 4000, 8000, 16000, 32000,
    64000, 125000, 250000, 500000, 1000000
]

# Вопросы. correct: индекс правильного ответа (0=A, 1=B, 2=C, 3=D)
QUESTIONS = [
    {"q": "Столица Франции?", "a": ["Лондон", "Париж", "Берлин", "Мадрид"], "correct": 1},
    {"q": "Химическая формула воды?", "a": ["CO2", "H2O", "NaCl", "O2"], "correct": 1},
    {"q": "Кто написал роман «Война и мир»?", "a": ["Достоевский", "Чехов", "Толстой", "Пушкин"], "correct": 2},
    {"q": "Сколько континентов на Земле?", "a": ["5", "6", "7", "8"], "correct": 1},
    {"q": "Какая планета Солнечной системы самая большая?", "a": ["Сатурн", "Юпитер", "Уран", "Нептун"], "correct": 1},
    {"q": "В каком году началась Великая Отечественная война?", "a": ["1939", "1941", "1942", "1945"], "correct": 1},
    {"q": "Какой элемент обозначается символом 'Au'?", "a": ["Серебро", "Золото", "Алюминий", "Аргон"], "correct": 1},
    {"q": "Кто изобрёл телефон?", "a": ["Тесла", "Эдисон", "Белл", "Маркони"], "correct": 2},
    {"q": "Сколько костей в теле взрослого человека?", "a": ["206", "300", "150", "250"], "correct": 0},
    {"q": "В какой стране находятся пирамиды Гизы?", "a": ["Ирак", "Египет", "Мексика", "Иран"], "correct": 1},
    {"q": "Какой газ составляет ~78% атмосферы Земли?", "a": ["Кислород", "Азот", "Углекислый газ", "Водород"],
     "correct": 1},
    {"q": "Кто написал картину «Мона Лиза»?", "a": ["Микеланджело", "Рафаэль", "Леонардо да Винчи", "Боттичелли"],
     "correct": 2},
    {"q": "В каком году Юрий Гагарин полетел в космос?", "a": ["1957", "1961", "1965", "1969"], "correct": 1},
    {"q": "Какой океан самый глубокий?", "a": ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"],
     "correct": 2},
    {"q": "Какая страна самая большая по площади?", "a": ["Канада", "США", "Китай", "Россия"], "correct": 3}
]

LEADERBOARD_FILE = "leaderboard.json"



# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ


def load_leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_leaderboard(board):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(board, f, ensure_ascii=False, indent=2)


def update_leaderboard(name, score):
    board = load_leaderboard()
    board.append({
        "name": name,
        "score": score,
        "date": datetime.now().strftime("%d.%m.%Y %H:%M")
    })
    board.sort(key=lambda x: x["score"], reverse=True)
    board = board[:10]
    save_leaderboard(board)
    return board


def display_leaderboard():
    board = load_leaderboard()
    print("\n🏆 ТАБЛИЦА РЕКОРДОВ 🏆")
    if not board:
        print("Пока нет записей. Станьте первым!")
    else:
        print(f"{'№':<3} | {'Имя':<15} | {'Выигрыш':<12} | {'Дата':<16}")
        print("-" * 52)
        for i, entry in enumerate(board, 1):
            print(f"{i:<3} | {entry['name']:<15} | {entry['score']:<12,} | {entry['date']:<16}")
    print()


def simulate_audience(correct_idx, available):
    correct_pct = random.randint(45, 75)
    remaining = 100 - correct_pct
    others = [i for i in available if i != correct_idx]
    res = {idx: 0 for idx in available}
    if not others:
        res[correct_idx] = 100
    else:
        base = remaining // len(others)
        for idx in others:
            res[idx] = base
        extra = remaining % len(others)
        for _ in range(extra):
            res[random.choice(others)] += 1
        res[correct_idx] = correct_pct
    return res


def simulate_friend(correct_idx, available):
    if random.random() < 0.75:
        guess = correct_idx
        conf = random.randint(70, 95)
    else:
        others = [i for i in available if i != correct_idx]
        guess = random.choice(others) if others else correct_idx
        conf = random.randint(40, 65)
    return guess, conf



# ИГРОВАЯ ЛОГИКА


def play_game(player_name):
    current_prize = 0
    # Состояние подсказок: True = доступна
    lifelines = {"50_50": True, "audience": True, "friend": True}
    # Маппинг: внутренний ключ -> (клавиша ввода, название для отображения)
    lifeline_info = {
        "50_50": ("1", "50 на 50"),
        "audience": ("2", "Помощь зала"),
        "friend": ("3", "Звонок другу")
    }

    print(f"\n🎮 Начинаем игру, {player_name}! Удачи!")
    print("Правила: 15 вопросов, 3 подсказки. На неправильный ответ игра заканчивается.")
    print("В любой момент введите 'выход', чтобы забрать текущий выигрыш.\n")

    for i, q in enumerate(QUESTIONS):
        prize_for_q = PRIZE_LADDER[i]
        print("=" * 50)
        print(f"📊 Вопрос {i + 1} из 15 | На кону: {prize_for_q:,} руб.")
        print(f"💰 Ваш текущий выигрыш: {current_prize:,} руб.")

        available = [0, 1, 2, 3]

        while True:
            print(f"\n❓ {q['q']}")
            for idx in range(4):
                if idx in available:
                    print(f"  {chr(65 + idx)}) {q['a'][idx]}")
                else:
                    print(f"  {chr(65 + idx)}) — (исключено)")

            active_lifelines = [
                f"{key}) {name}"
                for internal_key, (key, name) in lifeline_info.items()
                if lifelines[internal_key]
            ]
            if active_lifelines:
                print(f"🔍 Подсказки: {', '.join(active_lifelines)}")
            else:
                print("🔍 Подсказки закончились")

            try:
                cmd = input("\n👉 Ваш ответ (A/B/C/D), подсказка (1/2/3) или 'выход': ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\n\n🛑 Игра прервана. Сохраняем текущий выигрыш.")
                return current_prize

            if not cmd:
                continue

            # Обработка выхода
            if cmd in ("ВЫХОД", "Q", "STOP", "СТОП"):
                print(f"\n🛑 Вы решили остановиться. Ваш гарантированный выигрыш: {current_prize:,} руб.")
                return current_prize

            # Обработка подсказок
            if cmd in ("1", "2", "3"):
                internal_key = None
                for k, (key, name) in lifeline_info.items():
                    if key == cmd:
                        internal_key = k
                        break

                if internal_key and not lifelines[internal_key]:
                    print("⚠️ Эта подсказка уже использована!")
                    continue

                if internal_key:
                    lifelines[internal_key] = False
                    hint_name = lifeline_info[internal_key][1]
                    print(f"\n✨ Используем подсказку: {hint_name}")

                    if internal_key == "50_50":
                        wrong = [idx for idx in available if idx != q['correct']]
                        to_remove = random.sample(wrong, min(2, len(wrong)))
                        for r in to_remove:
                            if r in available:
                                available.remove(r)

                    elif internal_key == "audience":
                        stats = simulate_audience(q['correct'], available)
                        for idx, pct in sorted(stats.items()):
                            if pct > 0:
                                print(f"  📊 {chr(65 + idx)}: {pct}%")

                    elif internal_key == "friend":
                        guess, conf = simulate_friend(q['correct'], available)
                        print(f"  📞 Друг: «Я на {conf}% уверен, что это {chr(65 + guess)}»")
                continue

            # Обработка ответа
            if cmd in ("A", "B", "C", "D"):
                ans_idx = ord(cmd) - ord("A")
                if ans_idx not in available:
                    print("⛔ Этот вариант был исключён подсказкой. Выберите другой.")
                    continue

                if ans_idx == q['correct']:
                    current_prize = prize_for_q
                    print(f"\n✅ Правильно! Вы получаете {current_prize:,} руб.")
                    break  # Переход к следующему вопросу
                else:
                    print(f"\n❌ Неверно! Правильный ответ был: {q['a'][q['correct']]}")
                    print("💸 Игра окончена. Вы теряете весь выигрыш.")
                    return 0

            print("⚠️ Неверный ввод. Попробуйте снова.")

    print(f"\n🏆 ПОЗДРАВЛЯЕМ! Вы ответили на все 15 вопросов и стали миллионером!")
    return current_prize


# ГЛАВНЫЙ ЦИКЛ


def main():
    print("🌟 ДОБРО ПОЖАЛОВАТЬ В 'КТО ХОЧЕТ СТАТЬ МИЛЛИОНЕРОМ' 🌟")
    print("Создано Ибрагимом и Степой для PyCompanion\n")

    while True:
        print("\n1. Начать новую игру")
        print("2. Посмотреть таблицу рекордов")
        print("3. Выход")

        choice = input("Выберите действие (1/2/3): ").strip()

        if choice == "1":
            name = input("Введите ваше имя: ").strip()
            if not name:
                name = "Игрок"

            final_prize = play_game(name)
            if final_prize > 0:
                print(f"\n💾 Сохраняем результат {name}: {final_prize:,} руб.")
                update_leaderboard(name, final_prize)

        elif choice == "2":
            display_leaderboard()
        elif choice == "3":
            print("👋 Спасибо за игру! До новых встреч в PyCompanion!")
            break
        else:
            print("⚠️ Пожалуйста, введите 1, 2 или 3.")


if __name__ == "__main__":
    main()