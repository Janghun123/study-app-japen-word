import customtkinter as ctk
import os
import json
import random
from tkinter import Toplevel

# ✅ 파일 경로 상수
STAT_FILE = "quiz_stats.json"
WORD_FILE = "words.json"
SETTINGS_FILE = "settings.json"

# ✅ 초기 설정
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

# ✅ 단어 데이터 불러오기
DEFAULT_WORDS = []
if os.path.exists(WORD_FILE):
    with open(WORD_FILE, "r", encoding="utf-8") as f:
        DEFAULT_WORDS = [w for w in json.load(f) if w.get("word") and w.get("meaning") and not any(char.isdigit() for char in w["word"])]

# ✅ 사용자 설정 불러오기
USER_SETTINGS = {
    "dark_mode": True,
    "mode": "random",
    "show_pronunciation": False,
    "quiz_count": 10
}
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        USER_SETTINGS.update(json.load(f))

# ✅ 모드 설정
QUIZ_MODES = {
    "무작위": "random",
    "단어 → 뜻": "word_to_meaning",
    "뜻 → 단어": "meaning_to_word"
}

# ✅ 퀴즈 앱 클래스
class QuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("일본어 단어 퀴즈")
        self.geometry("500x800")
        self.configure(padx=20, pady=20)

        self.quiz_words = []
        self.quiz_items = []
        self.saved_words = []
        self.current_mode = USER_SETTINGS["mode"]
        self.show_pronunciation = USER_SETTINGS["show_pronunciation"]
        self.quiz_count = USER_SETTINGS["quiz_count"]

        ctk.CTkLabel(self, text="📘 일본어 퀴즈", font=("Arial", 20, "bold")).pack(pady=10)

        self.dark_mode_var = ctk.BooleanVar(value=USER_SETTINGS.get("dark_mode", True))
        ctk.CTkCheckBox(self, text="다크모드", variable=self.dark_mode_var, command=self.toggle_dark_mode).pack(anchor="ne", pady=(0,10))

        self.mode_var = ctk.StringVar(value=self.current_mode)
        self.mode_frame = ctk.CTkFrame(self)
        self.mode_frame.pack(pady=(0, 10))
        for text, mode in QUIZ_MODES.items():
            ctk.CTkRadioButton(self.mode_frame, text=text, variable=self.mode_var, value=mode, command=self.update_display_mode).pack(side="left", padx=5)

        self.count_entry = ctk.CTkEntry(self, placeholder_text="문제 수 (예: 10)", width=120)
        self.count_entry.insert(0, str(self.quiz_count))
        self.count_entry.pack(pady=(0, 5))

        ctk.CTkButton(self, text="발음 보기", command=self.toggle_pronunciation_display).pack(pady=(0, 10))

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=5)
        ctk.CTkButton(button_frame, text="퀴즈 생성", command=self.generate_quiz, width=120).grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_frame, text="오답 다시 풀기", command=self.retry_wrong_answers, width=120).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="통계 보기", command=self.show_stats, width=120).grid(row=0, column=2, padx=5)

        self.quiz_frame = ctk.CTkScrollableFrame(self, label_text="퀴즈 문제")
        self.quiz_frame.pack(fill="both", expand=True, pady=(10, 10))

        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=(5, 10))
        ctk.CTkButton(action_frame, text="정답 확인", command=self.check_answers, width=200).grid(row=0, column=0, padx=5)
        ctk.CTkButton(action_frame, text="다시 풀기", command=self.retry_current_items, width=200).grid(row=0, column=1, padx=5)

        self.generate_quiz()

    def toggle_dark_mode(self):
        mode = "Dark" if self.dark_mode_var.get() else "Light"
        ctk.set_appearance_mode(mode)

    def update_display_mode(self):
        self.current_mode = self.mode_var.get()
        self.refresh_quiz_items()

    def toggle_pronunciation_display(self):
        self.show_pronunciation = not self.show_pronunciation
        self.refresh_quiz_items()

    def generate_quiz(self):
        try:
            self.quiz_count = int(self.count_entry.get())
        except:
            self.quiz_count = USER_SETTINGS["quiz_count"]

        self.saved_words = random.sample(DEFAULT_WORDS, min(self.quiz_count, len(DEFAULT_WORDS)))
        self.refresh_quiz_items()

    def refresh_quiz_items(self):
        for widget in self.quiz_frame.winfo_children():
            widget.destroy()
        self.quiz_items = [QuizItem(self.quiz_frame, word_data, self.current_mode, self.show_pronunciation) for word_data in self.saved_words]
        for item in self.quiz_items:
            item.pack(fill="x", pady=5)

    def retry_wrong_answers(self):
        wrong_items = [item for item in self.quiz_items if not item.answered_correctly]
        self.saved_words = [item.word_data for item in wrong_items]
        self.refresh_quiz_items()

    def retry_current_items(self):
        self.refresh_quiz_items()

    def show_stats(self):
        correct = sum(item.answered_correctly for item in self.quiz_items)
        incorrect = len(self.quiz_items) - correct
        popup = Toplevel(self)
        popup.title("퀴즈 통계")
        popup.geometry("300x150")
        popup.configure(bg="#333333")
        label = ctk.CTkLabel(popup, text=f"정답: {correct}\n오답: {incorrect}", font=("Arial", 14))
        label.pack(padx=10, pady=20)

    def check_answers(self):
        for item in self.quiz_items:
            item.check_answer()


# ✅ 퀴즈 항목 클래스
class QuizItem(ctk.CTkFrame):
    def __init__(self, master, word_data, mode, show_pronunciation):
        super().__init__(master)
        self.word_data = word_data
        self.mode = mode
        self.show_pronunciation = show_pronunciation
        self.answered_correctly = False

        self.question, self.answer = self.prepare_question()

        question_text = self.question
        if show_pronunciation and word_data.get("pronunciation"):
            question_text += f" [{word_data['pronunciation']}]"

        self.label = ctk.CTkLabel(self, text=question_text, font=("Arial", 16), text_color="#3366cc")
        self.label.pack(side="left", padx=10)

        self.entry = ctk.CTkEntry(self, placeholder_text="정답 입력")
        self.entry.pack(side="left", fill="x", expand=True, padx=10)

        self.feedback_label = None

    def prepare_question(self):
        if self.mode == "word_to_meaning":
            return self.word_data["word"], self.word_data["meaning"]
        elif self.mode == "meaning_to_word":
            return self.word_data["meaning"], self.word_data["word"]
        else:
            if random.choice([True, False]):
                return self.word_data["word"], self.word_data["meaning"]
            else:
                return self.word_data["meaning"], self.word_data["word"]

    def check_answer(self):
        user_input = self.entry.get().strip()
        if self.feedback_label:
            self.feedback_label.destroy()

        if user_input == self.answer:
            self.answered_correctly = True
            self.feedback_label = ctk.CTkLabel(self, text="정답입니다!", text_color="green")
        else:
            self.feedback_label = ctk.CTkLabel(self, text=f"정답: {self.answer}", text_color="red")

        self.entry.pack_forget()
        self.feedback_label.pack(side="left", padx=10)


# ✅ 앱 실행
if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
