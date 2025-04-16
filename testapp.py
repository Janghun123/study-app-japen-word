import customtkinter as ctk
import os
import json
import random
from tkinter import Toplevel, StringVar
from datetime import datetime

# ✅ 다크모드 설정 초기값 (시스템 자동 또는 수동 토글 가능)
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

# ✅ 기본 단어 리스트 (100개로 확장됨) - 발음 포함
DEFAULT_WORDS = [
    ("学校", "학교", "がっこう"), ("先生", "선생님", "せんせい"), ("本", "책", "ほん"), ("学生", "학생", "がくせい"), ("日本", "일본", "にほん"),
    # ... (이하 생략)
    ("鍵", "열쇠", "かぎ"), ("地図", "지도", "ちず")
]

QUIZ_MODE_OPTIONS = ["단어 → 뜻", "뜻 → 단어", "무작위"]

APP_STATE = {
    "quiz_mode": QUIZ_MODE_OPTIONS[0],
    "show_pronunciation": False,
    "quiz_data": [],
    "quiz_direction": [],
    "dark_mode": True
}

class WordbookApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("📖 일본어 퀴즈 단어장")
        self.geometry("420x640")
        self.configure(padx=10, pady=10)

        self.current_widgets = []

        # ✅ 상단 바 통합 프레임
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.pack(fill="x", pady=(5, 0))

        self.mode_var = StringVar(value=APP_STATE["quiz_mode"])
        self.mode_menu = ctk.CTkOptionMenu(self.top_bar, variable=self.mode_var, values=QUIZ_MODE_OPTIONS, command=self.change_mode)
        self.mode_menu.pack(side="left", padx=(0, 5))

        self.pronounce_toggle = ctk.CTkButton(self.top_bar, text="👁️ 발음 보기", width=110, command=self.toggle_pronunciation)
        self.pronounce_toggle.pack(side="left", padx=(0, 5))

        self.theme_toggle = ctk.CTkSwitch(self.top_bar, text="다크모드", command=self.toggle_theme)
        self.theme_toggle.select()  # 기본 다크모드 ON
        self.theme_toggle.pack(side="right")

        # ✅ 퀴즈 컨트롤 버튼들
        self.check_button = ctk.CTkButton(self, text="정답 확인", command=self.check_all_answers)
        self.check_button.pack(fill="x", padx=5, pady=(10, 3))

        self.reset_button = ctk.CTkButton(self, text="퀴즈 초기화", command=self.reset_quiz_state)
        self.reset_button.pack(fill="x", padx=5, pady=(0, 3))

        self.generate_btn = ctk.CTkButton(self, text="새 퀴즈 생성", height=32, command=self.generate_quiz)
        self.generate_btn.pack(fill="x", padx=5, pady=(0, 8))

        self.quiz_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.quiz_frame.pack(fill="both", expand=True)

        self.generate_quiz()

    def toggle_pronunciation(self):
        APP_STATE["show_pronunciation"] = not APP_STATE["show_pronunciation"]
        for widget in self.current_widgets:
            if isinstance(widget, QuizItem):
                widget.update_pronunciation()

    def toggle_theme(self):
        APP_STATE["dark_mode"] = not APP_STATE["dark_mode"]
        mode = "Dark" if APP_STATE["dark_mode"] else "Light"
        ctk.set_appearance_mode(mode)
        self.update_quiz_display(refresh_direction=False)

    def change_mode(self, selected_mode):
        APP_STATE["quiz_mode"] = selected_mode
        self.generate_quiz()

    def generate_quiz(self):
        APP_STATE["quiz_data"] = random.sample(DEFAULT_WORDS, 5)
        APP_STATE["quiz_direction"] = []
        for _ in APP_STATE["quiz_data"]:
            if APP_STATE["quiz_mode"] == "무작위":
                APP_STATE["quiz_direction"].append(random.choice(["단어→뜻", "뜻→단어"]))
            else:
                APP_STATE["quiz_direction"].append(APP_STATE["quiz_mode"])
        self.update_quiz_display()

    def update_quiz_display(self, refresh_direction=True):
        for widget in self.current_widgets:
            widget.destroy()
        self.current_widgets.clear()

        for idx, (word, meaning, pronunciation) in enumerate(APP_STATE["quiz_data"]):
            if refresh_direction:
                mode = APP_STATE["quiz_mode"]
                if mode == "무작위":
                    mode = APP_STATE["quiz_direction"][idx] = random.choice(["단어→뜻", "뜻→단어"])
                else:
                    APP_STATE["quiz_direction"][idx] = mode
            else:
                mode = APP_STATE["quiz_direction"][idx]

            quiz = word if mode == "단어→뜻" else meaning
            answer = meaning if mode == "단어→뜻" else word

            quiz_box = QuizItem(self.quiz_frame, quiz, answer, pronunciation)
            quiz_box.pack(fill="x", padx=5, pady=4)
            self.current_widgets.append(quiz_box)

    def check_all_answers(self):
        for item in self.current_widgets:
            if isinstance(item, QuizItem):
                item.reveal_answer()

    def reset_quiz_state(self):
        self.generate_quiz()


class QuizItem(ctk.CTkFrame):
    def __init__(self, master, quiz, answer, pronunciation):
        super().__init__(master, corner_radius=10, border_width=1, border_color="#666")
        self.answer = answer
        self.pronunciation = pronunciation
        self.quiz = quiz

        bg_color = "#f0f0f0" if not APP_STATE["dark_mode"] else "#333"
        text_color = "black" if not APP_STATE["dark_mode"] else "white"

        self.configure(fg_color=bg_color)

        self.label = ctk.CTkLabel(self, text=quiz, anchor="w", font=("Arial", 16), text_color=text_color)
        self.label.grid(row=0, column=0, padx=10, sticky="w")

        self.entry = ctk.CTkEntry(self, placeholder_text="입력...")
        self.entry.grid(row=0, column=1, padx=10, sticky="ew")

        self.pronounce_label = ctk.CTkLabel(
            self,
            text=self.pronunciation if APP_STATE["show_pronunciation"] else "",
            font=("Arial", 12, "italic"),
            text_color="gray"
        )
        self.pronounce_label.grid(row=1, column=0, columnspan=2, padx=10, sticky="w")

        self.grid_columnconfigure(1, weight=1)

    def update_pronunciation(self):
        self.pronounce_label.configure(text=self.pronunciation if APP_STATE["show_pronunciation"] else "")

    def reveal_answer(self):
        user_input = self.entry.get().strip()
        if user_input == self.answer:
            self.label.configure(text_color="green")
            self.entry.destroy()
        else:
            self.label.configure(text_color="red")
            self.entry.destroy()
            wrong_label = ctk.CTkLabel(self, text=f"정답: {self.answer}", text_color="gray")
            wrong_label.grid(row=0, column=1, padx=10, sticky="w")


if __name__ == "__main__":
    app = WordbookApp()
    app.mainloop()
