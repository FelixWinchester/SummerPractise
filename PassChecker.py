import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
import re
import math

class PasswordChecker(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")  # Попробуйте другие темы: "equilux", "yaru", "breeze"
        
        # Настройки окна
        self.title("Анализатор сложности пароля")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Настройки для macOS
        self.tk.call('tk', 'scaling', 2.0)
        
        self.create_ui()
    
    def create_ui(self):
        # Стилизация
        style = ttk.Style()
        style.configure('TLabel', font=('Helvetica', 12))
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'))
        style.configure('Result.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('TButton', font=('Helvetica', 12))
        style.configure('TCheckbutton', font=('Helvetica', 12))
        
        # Заголовок
        self.title_label = ttk.Label(
            self, 
            text="Проверка сложности пароля",
            style='Title.TLabel'
        )
        self.title_label.pack(pady=20)
        
        # Поле ввода пароля
        self.password_frame = ttk.Frame(self)
        self.password_frame.pack(pady=10, padx=20, fill="x")
        
        self.password_var = tk.StringVar()
        self.password_var.trace_add("write", self.check_password)
        
        self.password_input = ttk.Entry(
            self.password_frame,
            textvariable=self.password_var,
            show="•",
            font=("Helvetica", 14)
        )
        self.password_input.pack(side="left", fill="x", expand=True)
        
        # Кнопка показать/скрыть пароль
        self.toggle_btn = ttk.Checkbutton(
            self.password_frame,
            text="Показать",
            command=self.toggle_password_visibility,
            style='Toolbutton'
        )
        self.toggle_btn.pack(side="right")
        
        # Индикатор сложности
        self.progress_frame = ttk.Frame(self)
        self.progress_frame.pack(pady=10, padx=20, fill="x")
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            orient="horizontal",
            length=400,
            mode="determinate",
            style='TProgressbar'
        )
        self.progress_bar.pack(fill="x")
        
        # Результаты проверки
        self.result_label = ttk.Label(
            self,
            text="Оценка сложности: ",
            style='Result.TLabel'
        )
        self.result_label.pack(pady=10)
        
        # Детали проверки
        self.details_frame = ttk.Frame(self)
        self.details_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.details_text = tk.Text(
            self.details_frame,
            height=8,
            wrap="word",
            font=("Menlo", 12),
            state="disabled",
            bg="#f5f6f7",
            fg="#333333",
            insertbackground="#333333",
            selectbackground="#4a6984",
            selectforeground="#ffffff"
        )
        self.details_text.pack(fill="both", expand=True)
        
        # Рекомендации
        self.recommendations = ttk.Label(
            self,
            text="",
            wraplength=460,
            justify="left",
            style='TLabel'
        )
        self.recommendations.pack(pady=10, padx=20)
        
        # Критерии сложного пароля
        criteria_text = """Критерии сложного пароля:
- Длина не менее 12 символов
- Содержит заглавные и строчные буквы
- Содержит цифры и специальные символы
- Не содержит словарных слов или личной информации
- Не содержит повторяющихся последовательностей"""
        
        self.criteria_label = ttk.Label(
            self,
            text=criteria_text,
            justify="left",
            style='TLabel'
        )
        self.criteria_label.pack(pady=10, padx=20)
    
    def toggle_password_visibility(self):
        if self.toggle_btn.instate(['selected']):
            self.password_input.config(show="")
            self.toggle_btn.config(text="Скрыть")
        else:
            self.password_input.config(show="•")
            self.toggle_btn.config(text="Показать")
    
    def check_password(self, *args):
        password = self.password_var.get()
        
        if not password:
            self.reset_display()
            return
            
        checks = {
            "Длина": self.check_length(password),
            "Регистр": self.check_case(password),
            "Цифры": self.check_digits(password),
            "Спецсимволы": self.check_special_chars(password),
            "Последовательности": self.check_sequences(password),
            "Шаблоны": self.check_common_patterns(password),
            "Энтропия": self.check_entropy(password)
        }
        
        total_score = sum(score for score, _ in checks.values())
        total_score = min(total_score, 100)
        self.update_display(total_score, checks)
    
    def reset_display(self):
        self.progress_bar["value"] = 0
        self.result_label["text"] = "Оценка сложности: "
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, "end")
        self.details_text.config(state="disabled")
        self.recommendations["text"] = ""
    
    def update_display(self, score, checks):
        self.progress_bar["value"] = score
        
        # Цвет прогрессбара в зависимости от оценки
        style = ttk.Style()
        if score < 40:
            style.configure("TProgressbar", background="#ff6b6b")  # Красный
            strength = "Очень слабый"
        elif score < 70:
            style.configure("TProgressbar", background="#ffa502")  # Оранжевый
            strength = "Средний"
        elif score < 90:
            style.configure("TProgressbar", background="#feca57")  # Желтый
            strength = "Хороший"
        else:
            style.configure("TProgressbar", background="#1dd1a1")  # Зеленый
            strength = "Отличный"
        
        self.result_label["text"] = f"Оценка сложности: {strength} ({score}/100)"
        
        details = ""
        for category, (score, feedback) in checks.items():
            details += f"✓ {category}: {feedback}\n"
        
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, "end")
        self.details_text.insert("end", details)
        self.details_text.config(state="disabled")
        
        if score < 40:
            self.recommendations["text"] = "Рекомендации: Ваш пароль слишком слабый. Увеличьте длину, добавьте разные типы символов."
        elif score < 70:
            self.recommendations["text"] = "Рекомендации: Пароль можно улучшить. Попробуйте увеличить длину, добавить больше специальных символов."
        elif score < 90:
            self.recommendations["text"] = "Рекомендации: Хороший пароль, но можно сделать еще лучше."
        else:
            self.recommendations["text"] = "Рекомендации: Отличный пароль! Соответствует всем критериям сложности."

    # Методы проверки остаются без изменений
    def check_length(self, password):
        length = len(password)
        if length < 8: return 0, f"Слишком короткий ({length} символов)"
        elif length < 12: return 10, f"Минимально допустимый ({length})"
        elif length < 16: return 20, f"Хорошо ({length})"
        else: return 25, f"Отлично ({length})"
    
    def check_case(self, password):
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        if not has_lower and not has_upper: return 0, "Нет букв"
        elif has_lower and not has_upper: return 5, "Только строчные"
        elif has_upper and not has_lower: return 5, "Только заглавные"
        else: return 15, "Есть оба регистра"
    
    def check_digits(self, password):
        digit_count = sum(c.isdigit() for c in password)
        if digit_count == 0: return 0, "Нет цифр"
        elif digit_count == 1: return 5, "Только 1 цифра"
        elif digit_count < 3: return 10, f"{digit_count} цифры"
        else: return 15, f"Хорошо ({digit_count} цифр)"
    
    def check_special_chars(self, password):
        special_chars = re.compile(r'[!@#$%^&*(),.?":{}|<>]')
        special_count = len(special_chars.findall(password))
        if special_count == 0: return 0, "Нет спецсимволов"
        elif special_count == 1: return 5, "Только 1 спецсимвол"
        elif special_count < 3: return 10, f"{special_count} спецсимвола"
        else: return 15, f"Отлично ({special_count})"
    
    def check_sequences(self, password):
        sequences = ["0123456789", "9876543210", "qwertyuiop", "asdfghjkl", "zxcvbnm"]
        password_lower = password.lower()
        for seq in sequences:
            if seq in password_lower or seq[::-1] in password_lower:
                return 0, f"Простая последовательность '{seq[:3]}...'"
        if re.search(r'(.)\1{2,}', password_lower):
            return 0, "Повторяющиеся символы"
        return 15, "Нет простых последовательностей"
    
    def check_common_patterns(self, password):
        common_passwords = ["password", "123456", "qwerty", "admin", "пароль"]
        password_lower = password.lower()
        for common in common_passwords:
            if common in password_lower:
                return 0, f"Распространенный пароль '{common}'"
        if re.search(r'(19|20)\d{2}', password):
            return 0, "Содержит год"
        if any(word in password_lower for word in ["user", "login", "secret"]):
            return 5, "Словарные слова"
        return 15, "Нет распространенных шаблонов"
    
    def check_entropy(self, password):
        char_types = 0
        if any(c.islower() for c in password): char_types += 26
        if any(c.isupper() for c in password): char_types += 26
        if any(c.isdigit() for c in password): char_types += 10
        if re.search(r'[^a-zA-Z0-9]', password): char_types += 32
        if char_types == 0: return 0, "Невозможно оценить"
        entropy = len(password) * (char_types ** 0.5)
        if entropy < 30: return 0, f"Очень низкая ({entropy:.1f})"
        elif entropy < 50: return 5, f"Низкая ({entropy:.1f})"
        elif entropy < 70: return 10, f"Средняя ({entropy:.1f})"
        else: return 15, f"Высокая ({entropy:.1f})"

if __name__ == "__main__":
    app = PasswordChecker()
    app.mainloop()
