import customtkinter as ctk
import os
import json
import random
import tkinter.font as tkfont
from tkinter import Toplevel

STAT_FILE = "quiz_stats.json"
WORD_FILE = "words.json"
SETTINGS_FILE = "settings.json"
# color mode = basic 
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")
# basic color = dark mode
DEFAULT_WORDS = [] # 기본 단어
# 파일 불러오기기
if os.path.exists(WORD_FILE):
    with open(WORD_FILE, "r", encoding="utf-8") as f:
        DEFAULT_WORDS = [w for w in json.load(f) if w.get("word") and w.get("meaning") and not any(char.isdigit() for char in w["word"])]

USER_SETTINGS = {
    "dark_mode": True,
    "mode": "random",
    "show_pronunciation": False,
    "quiz_count": 10,
    "font_name": "Arial",
    "font_size": 14
}
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        USER_SETTINGS.update(json.load(f))

def get_custom_font(weight="normal"):
    size = USER_SETTINGS.get("font_size", 14)
    name = USER_SETTINGS.get("font_name", "Arial")
    return (name, size, weight)

QUIZ_MODES = {
    "무작위": "random",
    "단어 → 뜻": "word_to_meaning",
    "뜻 → 단어": "meaning_to_word"
}

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

        ctk.CTkLabel(self, text="📘 일본어 퀴즈", font=get_custom_font("bold")).pack(pady=10)

        self.dark_mode_var = ctk.BooleanVar(value=USER_SETTINGS.get("dark_mode", True))
        ctk.CTkCheckBox(self, text="다크모드", variable=self.dark_mode_var, command=self.toggle_dark_mode, font=get_custom_font()).pack(anchor="ne", pady=(0,10))

        self.mode_var = ctk.StringVar(value=self.current_mode)
        self.mode_frame = ctk.CTkFrame(self)
        self.mode_frame.pack(pady=(0, 10))
        for text, mode in QUIZ_MODES.items():
            ctk.CTkRadioButton(self.mode_frame, text=text, variable=self.mode_var, value=mode, command=self.update_display_mode, font=get_custom_font()).pack(side="left", padx=5)

        self.count_entry = ctk.CTkEntry(self, placeholder_text="문제 수 (예: 10)", width=120, font=get_custom_font())
        self.count_entry.insert(0, str(self.quiz_count))
        self.count_entry.pack(pady=(0, 5))

        top_button_frame = ctk.CTkFrame(self)
        top_button_frame.pack(pady=(0, 10))

        ctk.CTkButton(top_button_frame, text="발음 보기", command=self.toggle_pronunciation_display, font=get_custom_font()).pack(side="left", padx=5)
        ctk.CTkButton(top_button_frame, text="설정", command=self.open_settings, font=get_custom_font()).pack(side="left", padx=5)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=5)

        ctk.CTkButton(button_frame, text="퀴즈 생성", command=self.generate_quiz_from_count_entry, width=140, font=get_custom_font()).grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_frame, text="오답 다시 풀기", command=self.retry_wrong_answers, width=140, font=get_custom_font()).grid(row=0, column=1, padx=5)
        ctk.CTkButton(button_frame, text="통계 보기", command=self.show_stats, width=140, font=get_custom_font()).grid(row=0, column=2, padx=5)

        self.quiz_frame = ctk.CTkScrollableFrame(self, label_text="퀴즈 문제")
        self.quiz_frame.pack(fill="both", expand=True, pady=(10, 10))

        action_frame = ctk.CTkFrame(self)
        action_frame.pack(pady=(5, 10))
        ctk.CTkButton(action_frame, text="정답 확인", command=self.check_answers, width=200, font=get_custom_font()).grid(row=0, column=0, padx=5)
        ctk.CTkButton(action_frame, text="다시 풀기", command=self.retry_current_items, width=200, font=get_custom_font()).grid(row=0, column=1, padx=5)

        self.generate_quiz_from_count_entry()

    def toggle_dark_mode(self):
        mode = "Dark" if self.dark_mode_var.get() else "Light"
        ctk.set_appearance_mode(mode)
        self.refresh_quiz_items()

    def update_display_mode(self):
        self.current_mode = self.mode_var.get()
        self.refresh_quiz_items()

    def toggle_pronunciation_display(self):
        self.show_pronunciation = not self.show_pronunciation
        self.refresh_quiz_items()

    def generate_quiz_from_count_entry(self):
        try:
            self.quiz_count = int(self.count_entry.get())
        except:
            self.quiz_count = USER_SETTINGS["quiz_count"]
        self.generate_quiz()

    def generate_quiz(self):
        seen = set()
        unique_words = []
        for word_data in DEFAULT_WORDS:
            key = (word_data["word"], word_data["meaning"])
            if key not in seen:
                seen.add(key)
                unique_words.append(word_data)

        self.saved_words = random.sample(unique_words, min(self.quiz_count, len(unique_words)))
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
        total = correct + incorrect
        ratio = (correct / total * 100) if total > 0 else 0

        popup = Toplevel(self)
        popup.title("퀴즈 통계")
        popup.geometry("300x160")
        popup.configure(bg="#333333")
        text = f"정답: {correct}\n오답: {incorrect}\n정답률: {ratio:.1f}%"
        label = ctk.CTkLabel(popup, text=text, font=get_custom_font())
        label.pack(padx=10, pady=20)

    def check_answers(self):
        for item in self.quiz_items:
            item.check_answer()

    def open_settings(self):
        SettingsWindow(self)

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

        self.label = ctk.CTkLabel(self, text=question_text, font=get_custom_font())
        self.label.pack(side="left", padx=10)
        self.update_label_color()

        self.entry = ctk.CTkEntry(self, placeholder_text="정답 입력", font=get_custom_font())
        self.entry.pack(side="left", fill="x", expand=True, padx=10)

        self.feedback_label = None

    def update_label_color(self):
        mode = ctk.get_appearance_mode()
        color = "#ffffff" if mode == "Dark" else "#222222"
        self.label.configure(text_color=color)

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
        user_input = self.entry.get().strip().lower()
        correct_answer = self.answer.strip().lower()
        if self.feedback_label:
            self.feedback_label.destroy()

        if user_input == correct_answer:
            self.answered_correctly = True
            self.feedback_label = ctk.CTkLabel(self, text="정답입니다!", text_color="green", font=get_custom_font())
        else:
            self.feedback_label = ctk.CTkLabel(self, text=f"정답: {self.answer}", text_color="red", font=get_custom_font())

        self.entry.pack_forget()
        self.feedback_label.pack(side="left", padx=10)

import tkinter.font as tkfont

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("설정")
        self.geometry("300x280")
        self.resizable(False, False)

        self.master = master

        # ✅ 세로쓰기 전용 폰트 제거
        all_fonts = sorted([f for f in tkfont.families() if not f.startswith("@")])
        filtered_fonts = [f for f in all_fonts if any(c in f.lower() for c in ['arial', 'gulim', 'malgun', 'times', 'courier', '돋움', '바탕', '나눔'])]

        ctk.CTkLabel(self, text="폰트 종류", font=get_custom_font("bold")).pack(pady=(10, 5))
        self.font_optionmenu = ctk.CTkOptionMenu(self, values=filtered_fonts or all_fonts[:30])
        self.font_optionmenu.set(USER_SETTINGS.get("font_name", "Arial"))
        self.font_optionmenu.pack(pady=(0, 10))

        ctk.CTkLabel(self, text="폰트 크기", font=get_custom_font("bold")).pack(pady=(5, 5))
        self.font_slider = ctk.CTkSlider(self, from_=10, to=30, number_of_steps=20)
        self.font_slider.set(USER_SETTINGS.get("font_size", 14))
        self.font_slider.pack(pady=(0, 20))

        # ✅ 슬라이더 위에서만 마우스 휠 활성화
        self.font_slider.bind("<Enter>", self.activate_wheel)
        self.font_slider.bind("<Leave>", self.deactivate_wheel)

        ctk.CTkButton(self, text="저장", command=self.save_settings, font=get_custom_font()).pack(pady=(5, 10))

    def activate_wheel(self, _):
        self.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def deactivate_wheel(self, _):
        self.unbind_all("<MouseWheel>")

    def on_mouse_wheel(self, event):
        delta = 1 if event.delta > 0 else -1
        current = self.font_slider.get()
        new_val = max(10, min(30, current + delta))
        self.font_slider.set(new_val)

    def save_settings(self):
        USER_SETTINGS["font_name"] = self.font_optionmenu.get()
        USER_SETTINGS["font_size"] = int(self.font_slider.get())

        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(USER_SETTINGS, f, ensure_ascii=False, indent=2)

        self.master.refresh_quiz_items()
        self.destroy()


if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
