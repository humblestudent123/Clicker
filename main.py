import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time

mouse = Controller()
clicking = False
hold_time = 3.0           # удержание ЛКМ
wait_after_hold = 2.0     # ожидание после удержания
fast_click_time = 5.0     # быстрые клики
click_interval = 0.2      # интервал между быстрыми кликами
cycle_interval = 3.0      # время перед повтором цикла
thread = None

# Горячие клавиши по умолчанию
start_key = keyboard.Key.f6
pause_key = keyboard.Key.f7

def fast_click_for_duration(duration):
    end_time = time.time() + duration
    while clicking and time.time() < end_time:
        mouse.click(Button.left, 1)
        time.sleep(click_interval)

def start_sequence():
    global clicking, thread
    if clicking:
        return
    clicking = True
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")

    def cycle_loop():
        while clicking:
            # 1. Удержание ЛКМ
            status_bar.config(text=f"Удержание ЛКМ {hold_time} сек")
            mouse.press(Button.left)
            time.sleep(hold_time)
            mouse.release(Button.left)

            # 2. Ожидание после удержания
            status_bar.config(text=f"Ожидание {wait_after_hold} сек")
            time.sleep(wait_after_hold)

            # 3. Быстрые клики
            status_bar.config(text=f"Быстрые клики {fast_click_time} сек")
            fast_click_for_duration(fast_click_time)

            # 4. Интервал перед повтором
            status_bar.config(text=f"Интервал перед повтором {cycle_interval} сек")
            time.sleep(cycle_interval)

        # когда остановлено
        status_bar.config(text="Кликер остановлен")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")

    thread = threading.Thread(target=cycle_loop, daemon=True)
    thread.start()

def stop_clicking():
    global clicking
    clicking = False

# Настройки
def set_hold_time():
    global hold_time
    try:
        hold_time = float(entry_hold.get())
        status_bar.config(text=f"Удержание ЛКМ: {hold_time} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

def set_wait_after_hold():
    global wait_after_hold
    try:
        wait_after_hold = float(entry_wait.get())
        status_bar.config(text=f"Ожидание после удержания: {wait_after_hold} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

def set_fast_click_time():
    global fast_click_time
    try:
        fast_click_time = float(entry_fast_click.get())
        status_bar.config(text=f"Время быстрых кликов: {fast_click_time} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

def set_click_interval():
    global click_interval
    try:
        click_interval = float(entry_interval.get())
        status_bar.config(text=f"Интервал между быстрыми кликами: {click_interval} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

def set_cycle_interval():
    global cycle_interval
    try:
        cycle_interval = float(entry_cycle.get())
        status_bar.config(text=f"Интервал перед повтором: {cycle_interval} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

# Горячие клавиши
def key_to_str(key):
    try:
        return key.char
    except AttributeError:
        s = str(key)
        if s.startswith("Key."):
            return s.split(".",1)[1]
        return s

def on_press_global(key):
    if key_to_str(key) == key_to_str(start_key):
        start_sequence()
    elif key_to_str(key) == key_to_str(pause_key):
        stop_clicking()

def set_start_key():
    status_label.config(text="Нажмите клавишу для СТАРТА...")
    def on_press_once(key):
        global start_key
        start_key = key
        status_label.config(text=f"Старт = {key_to_str(start_key)}")
        return False
    threading.Thread(target=lambda: keyboard.Listener(on_press=on_press_once).start(), daemon=True).start()

def set_pause_key():
    status_label.config(text="Нажмите клавишу для ПАУЗЫ...")
    def on_press_once(key):
        global pause_key
        pause_key = key
        status_label.config(text=f"Пауза = {key_to_str(pause_key)}")
        return False
    threading.Thread(target=lambda: keyboard.Listener(on_press=on_press_once).start(), daemon=True).start()

global_listener = keyboard.Listener(on_press=on_press_global)
global_listener.daemon = True
global_listener.start()

# ---------- GUI ----------
root = tk.Tk()
root.title("Циклический автокликер")
root.geometry("480x480")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=6, pady=6)

# Вкладка кликера
frame1 = tk.Frame(notebook)
notebook.add(frame1, text="Кликер")

start_btn = tk.Button(frame1, text="Старт", width=25, command=start_sequence)
start_btn.pack(pady=5)

stop_btn = tk.Button(frame1, text="Стоп", width=25, command=stop_clicking, state="disabled")
stop_btn.pack(pady=5)

# Настройки
tk.Label(frame1, text="Удержание ЛКМ (сек):").pack(pady=2)
entry_hold = tk.Entry(frame1)
entry_hold.insert(0, "3.0")
entry_hold.pack()
tk.Button(frame1, text="Применить", command=set_hold_time).pack(pady=2)

tk.Label(frame1, text="Ожидание после удержания (сек):").pack(pady=2)
entry_wait = tk.Entry(frame1)
entry_wait.insert(0, "2.0")
entry_wait.pack()
tk.Button(frame1, text="Применить", command=set_wait_after_hold).pack(pady=2)

tk.Label(frame1, text="Время быстрых кликов (сек):").pack(pady=2)
entry_fast_click = tk.Entry(frame1)
entry_fast_click.insert(0, "5.0")
entry_fast_click.pack()
tk.Button(frame1, text="Применить", command=set_fast_click_time).pack(pady=2)

tk.Label(frame1, text="Интервал между быстрыми кликами (сек):").pack(pady=2)
entry_interval = tk.Entry(frame1)
entry_interval.insert(0, "0.2")
entry_interval.pack()
tk.Button(frame1, text="Применить", command=set_click_interval).pack(pady=2)

tk.Label(frame1, text="Интервал перед повтором цикла (сек):").pack(pady=2)
entry_cycle = tk.Entry(frame1)
entry_cycle.insert(0, "3.0")
entry_cycle.pack()
tk.Button(frame1, text="Применить", command=set_cycle_interval).pack(pady=2)

# Вкладка горячих клавиш
frame2 = tk.Frame(notebook)
notebook.add(frame2, text="Горячие клавиши")

tk.Button(frame2, text="Задать кнопку СТАРТ", command=set_start_key).pack(pady=10)
tk.Button(frame2, text="Задать кнопку ПАУЗА", command=set_pause_key).pack(pady=10)

status_label = tk.Label(frame2, text=f"Старт = {key_to_str(start_key)}  |  Пауза = {key_to_str(pause_key)}")
status_label.pack(pady=6)

# Статус бар
status_bar = tk.Label(root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
