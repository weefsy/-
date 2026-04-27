"""
Currency Converter GUI Application
Автор: [Ваше Имя]
Требования: Python 3.6+, tkinter (встроенный)
Не требует установки дополнительных библиотек
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import urllib.request
import urllib.error

# ---------------------------- API Configuration -------------------------------
API_URL = "https://api.exchangerate-api.com/v4/latest/{base_currency}"


def fetch_exchange_rate(base_currency, target_currency):
    """
    Получение курса обмена с exchangerate-api.com (бесплатно, ключ не требуется).
    Возвращает курс как float или вызывает исключение.
    """
    try:
        url = API_URL.format(base_currency=base_currency)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            rate = data['rates'].get(target_currency)
            if rate is None:
                raise ValueError(f"Валюта {target_currency} недоступна.")
            return float(rate)
    except urllib.error.URLError as e:
        raise Exception(f"Ошибка API: {e}")
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise Exception(f"Ошибка данных: {e}")


# ---------------------------- History Manager ---------------------------------
HISTORY_FILE = "conversion_history.json"


def load_history():
    """Загрузка истории конвертации из JSON файла."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """Сохранение истории конвертации в JSON файл."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_history_entry(history, from_curr, to_curr, amount, result, rate):
    """Добавление новой записи в историю и сохранение."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_curr,
        "to": to_curr,
        "amount": amount,
        "converted_amount": result,
        "rate": rate
    }
    history.insert(0, entry)  # новые записи в начале
    # Оставляем последние 50 записей
    if len(history) > 50:
        history.pop()
    save_history(history)
    return entry


# ---------------------------- GUI Application ---------------------------------
class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("750x550")
        self.root.resizable(True, True)

        # Загрузка истории
        self.history = load_history()

        # Список валют
        self.currencies = [
            "USD", "EUR", "RUB", "GBP", "JPY", "CAD", "CHF", "CNY",
            "INR", "AUD", "BRL", "TRY", "KRW", "MXN", "ZAR", "UAH", "KZT"
        ]

        # Построение GUI
        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Фрейм конвертации ---
        conv_frame = ttk.LabelFrame(main_frame, text="Конвертация", padding="10")
        conv_frame.pack(fill=tk.X, pady=5)

        # Из валюты
        ttk.Label(conv_frame, text="Из:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.from_currency = tk.StringVar(value="USD")
        from_combo = ttk.Combobox(conv_frame, textvariable=self.from_currency,
                                  values=self.currencies, state="readonly", width=10)
        from_combo.grid(row=0, column=1, padx=5, pady=5)

        # В валюту
        ttk.Label(conv_frame, text="В:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.to_currency = tk.StringVar(value="RUB")
        to_combo = ttk.Combobox(conv_frame, textvariable=self.to_currency,
                                values=self.currencies, state="readonly", width=10)
        to_combo.grid(row=0, column=3, padx=5, pady=5)

        # Поле ввода суммы
        ttk.Label(conv_frame, text="Сумма:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.amount_entry = ttk.Entry(conv_frame, width=20)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=1)

        # Кнопка конвертации
        self.convert_btn = ttk.Button(conv_frame, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=1, column=2, padx=5, pady=5)

        # Результат
        self.result_label = ttk.Label(conv_frame, text="Результат: --", font=('Arial', 10, 'bold'))
        self.result_label.grid(row=1, column=3, padx=5, pady=5)

        # --- Фрейм истории ---
        hist_frame = ttk.LabelFrame(main_frame, text="История конвертаций (последние 50)", padding="10")
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Таблица для истории
        columns = ("Timestamp", "From", "To", "Amount", "Converted", "Rate")
        self.history_tree = ttk.Treeview(hist_frame, columns=columns, show="headings", height=15)

        # Заголовки на русском
        self.history_tree.heading("Timestamp", text="Дата/Время")
        self.history_tree.heading("From", text="Из")
        self.history_tree.heading("To", text="В")
        self.history_tree.heading("Amount", text="Сумма")
        self.history_tree.heading("Converted", text="Результат")
        self.history_tree.heading("Rate", text="Курс")

        # Ширина колонок
        self.history_tree.column("Timestamp", width=140)
        self.history_tree.column("From", width=60)
        self.history_tree.column("To", width=60)
        self.history_tree.column("Amount", width=100)
        self.history_tree.column("Converted", width=100)
        self.history_tree.column("Rate", width=80)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(hist_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Кнопки управления историей
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.clear_btn = ttk.Button(btn_frame, text="Очистить историю", command=self.clear_history)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        self.refresh_btn = ttk.Button(btn_frame, text="Проверить API", command=self.test_api)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)

        # Привязка клавиши Enter к конвертации
        self.amount_entry.bind('<Return>', lambda event: self.convert())

    def convert(self):
        """Выполнение конвертации с проверкой ввода."""
        # Проверка ввода: сумма должна быть положительным числом
        amount_str = self.amount_entry.get().strip()
        if not amount_str:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите сумму.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной.")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректная сумма: {e}")
            return

        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()

        # Если валюты одинаковые
        if from_curr == to_curr:
            result = amount
            rate = 1.0
            self.result_label.config(text=f"Результат: {result:.2f} {to_curr}")
            add_history_entry(self.history, from_curr, to_curr, amount, result, rate)
            self.update_history_table()
            return

        # Получение курса обмена из API
        try:
            rate = fetch_exchange_rate(from_curr, to_curr)
            result = amount * rate
            self.result_label.config(text=f"Результат: {result:.2f} {to_curr}")

            # Сохранение в историю
            add_history_entry(self.history, from_curr, to_curr, amount, result, rate)
            self.update_history_table()

        except Exception as e:
            messagebox.showerror("Ошибка API", f"Не удалось получить курс обмена:\n{e}")

    def update_history_table(self):
        """Обновление таблицы истории."""
        # Очистка существующих элементов
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Вставка записей
        for entry in self.history:
            self.history_tree.insert("", tk.END, values=(
                entry["timestamp"],
                entry["from"],
                entry["to"],
                f"{entry['amount']:.2f}",
                f"{entry['converted_amount']:.2f}",
                f"{entry['rate']:.4f}"
            ))

    def clear_history(self):
        """Очистка истории после подтверждения."""
        if messagebox.askyesno("Очистка истории", "Вы уверены, что хотите удалить всю историю конвертаций?"):
            self.history = []
            save_history(self.history)
            self.update_history_table()
            self.result_label.config(text="Результат: --")
            messagebox.showinfo("История очищена", "Все записи истории удалены.")

    def test_api(self):
        """Проверка соединения с API."""
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        try:
            rate = fetch_exchange_rate(from_curr, to_curr)
            messagebox.showinfo("Проверка API",
                                f"Текущий курс из {from_curr} в {to_curr}:\n"
                                f"1 {from_curr} = {rate:.4f} {to_curr}\n\n"
                                f"API работает корректно.")
        except Exception as e:
            messagebox.showerror("Ошибка API", str(e))


# ---------------------------- Main Execution ---------------------------------
def main():
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()