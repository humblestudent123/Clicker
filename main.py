import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput import keyboard
import threading
import time

# --- Логика кликера ---
mouse = Controller()
clicking = False
hold_time = 3.0
wait_after_hold = 2.0
fast_click_time = 5.0
click_interval = 0.2
cycle_interval = 3.0
thread = None

start_key = keyboard.Key.f6
pause_key = keyboard.Key.f7

def fast_click_for_duration(duration):
    end_time = time.time() + duration
    while clicking and time.time() < end_time:
        mouse.click(Button.left, 1)
        time.sleep(click_interval)

def start_sequence():
    global clicking, thread
    if clicking: return
    clicking = True
    start_btn.config(state="disabled")
    stop_btn.config(state="normal")

    def cycle_loop():
        while clicking:
            status_bar.config(text=f"Удержание ЛКМ {hold_time} сек")
            mouse.press(Button.left)
            time.sleep(hold_time)
            mouse.release(Button.left)

            status_bar.config(text=f"Ожидание {wait_after_hold} сек")
            time.sleep(wait_after_hold)

            status_bar.config(text=f"Быстрые клики {fast_click_time} сек")
            fast_click_for_duration(fast_click_time)

            status_bar.config(text=f"Интервал перед повтором {cycle_interval} сек")
            time.sleep(cycle_interval)

        status_bar.config(text="Кликер остановлен")
        start_btn.config(state="normal")
        stop_btn.config(state="disabled")

    thread = threading.Thread(target=cycle_loop, daemon=True)
    thread.start()

def stop_clicking():
    global clicking
    clicking = False

# --- Настройки ---
def set_value(entry, var, label_text):
    try:
        value = float(entry.get())
        globals()[var] = value
        status_bar.config(text=f"{label_text}: {value} сек")
    except ValueError:
        status_bar.config(text="Ошибка: введите число")

# --- Горячие клавиши ---
def key_to_str(key):
    try: return key.char
    except AttributeError:
        s = str(key)
        if s.startswith("Key."): return s.split(".",1)[1]
        return s

def on_press_global(key):
    if key_to_str(key) == key_to_str(start_key): start_sequence()
    elif key_to_str(key) == key_to_str(pause_key): stop_clicking()

def set_hotkey(label, attr):
    label.config(text=f"Нажмите клавишу для {attr.upper()}...")
    def on_press_once(key):
        globals()[attr] = key
        label.config(text=f"{attr.capitalize()} = {key_to_str(key)}")
        return False
    threading.Thread(target=lambda: keyboard.Listener(on_press=on_press_once).start(), daemon=True).start()

global_listener = keyboard.Listener(on_press=on_press_global)
global_listener.daemon = True
global_listener.start()

# --- GUI ---
root = tk.Tk()
root.title("💎 Кликер 3-ступени с циклом")
root.geometry("500x550")
root.configure(bg="#2b2b2b")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", background="#444", foreground="white", padding=[12,5])
style.configure("TFrame", background="#2b2b2b")
style.configure("TButton", padding=6, font=("Helvetica", 11, "bold"))

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# --- Вкладка Кликера ---
frame_clicker = ttk.Frame(notebook)
notebook.add(frame_clicker, text="🚀 Кликер")

start_btn = tk.Button(frame_clicker, text="СТАРТ", bg="#4CAF50", fg="white", font=("Helvetica", 14, "bold"),
                      activebackground="#45a049", command=start_sequence)
start_btn.pack(pady=10, ipadx=20, ipady=5)

stop_btn = tk.Button(frame_clicker, text="СТОП", bg="#f44336", fg="white", font=("Helvetica", 14, "bold"),
                     activebackground="#d32f2f", command=stop_clicking, state="disabled")
stop_btn.pack(pady=10, ipadx=20, ipady=5)

# Настройки в карточках
def add_setting_card(parent, text, default, var_name):
    card = tk.Frame(parent, bg="#3c3c3c", bd=2, relief=tk.RIDGE)
    card.pack(fill="x", pady=5, padx=10)
    tk.Label(card, text=text, bg="#3c3c3c", fg="white", font=("Helvetica", 10)).pack(side="left", padx=5, pady=5)
    entry = tk.Entry(card, width=6)
    entry.insert(0, str(default))
    entry.pack(side="left", padx=5)
    tk.Button(card, text="Применить", bg="#607d8b", fg="white",
              command=lambda e=entry,v=var_name,t=text: set_value(e,v,t)).pack(side="left", padx=5)
    return entry

entry_hold = add_setting_card(frame_clicker, "Удержание ЛКМ (сек):", hold_time, "hold_time")
entry_wait = add_setting_card(frame_clicker, "Ожидание после удержания (сек):", wait_after_hold, "wait_after_hold")
entry_fast_click = add_setting_card(frame_clicker, "Время быстрых кликов (сек):", fast_click_time, "fast_click_time")
entry_interval = add_setting_card(frame_clicker, "Интервал между кликами (сек):", click_interval, "click_interval")
entry_cycle = add_setting_card(frame_clicker, "Интервал перед повтором (сек):", cycle_interval, "cycle_interval")

# --- Вкладка Горячих клавиш ---
frame_hotkeys = ttk.Frame(notebook)
notebook.add(frame_hotkeys, text="⌨ Горячие клавиши")

start_label = tk.Label(frame_hotkeys, text=f"Старт = {key_to_str(start_key)}", bg="#2b2b2b", fg="white", font=("Helvetica", 12))
start_label.pack(pady=10)
tk.Button(frame_hotkeys, text="Задать кнопку СТАРТ", bg="#4CAF50", fg="white",
          command=lambda: set_hotkey(start_label, "start_key")).pack(pady=5, ipadx=10)

pause_label = tk.Label(frame_hotkeys, text=f"Пауза = {key_to_str(pause_key)}", bg="#2b2b2b", fg="white", font=("Helvetica", 12))
pause_label.pack(pady=10)
tk.Button(frame_hotkeys, text="Задать кнопку ПАУЗА", bg="#f44336", fg="white",
          command=lambda: set_hotkey(pause_label, "pause_key")).pack(pady=5, ipadx=10)

# --- Статус-бар ---
status_bar = tk.Label(root, text="Готов", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#1e1e1e", fg="white")
status_bar.pack(side="bottom", fill="x")

root.mainloop()



































import json
import os

SETTINGS_FILE = "settings.json"

def save_settings():
    data = {
        "hold_time": hold_time,
        "wait_after_hold": wait_after_hold,
        "fast_click_time": fast_click_time,
        "click_interval": click_interval,
        "cycle_interval": cycle_interval,
        "start_key": str(start_key),
        "pause_key": str(pause_key)
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_settings():
    global hold_time, wait_after_hold, fast_click_time, click_interval, cycle_interval
    global start_key, pause_key
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return  # пустой файл, ничего не загружаем
                data = json.loads(content)
            hold_time = data.get("hold_time", hold_time)
            wait_after_hold = data.get("wait_after_hold", wait_after_hold)
            fast_click_time = data.get("fast_click_time", fast_click_time)
            click_interval = data.get("click_interval", click_interval)
            cycle_interval = data.get("cycle_interval", cycle_interval)

            start_key_str = data.get("start_key", str(start_key))
            pause_key_str = data.get("pause_key", str(pause_key))

            from pynput.keyboard import Key
            if start_key_str.startswith("Key."): start_key = getattr(Key, start_key_str.split(".")[1])
            else: start_key = start_key_str
            if pause_key_str.startswith("Key."): pause_key = getattr(Key, pause_key_str.split(".")[1])
            else: pause_key = pause_key_str

        except (json.JSONDecodeError, AttributeError):
            print("Файл settings.json поврежден или пустой, используются стандартные настройки.")


# В главном коде Tkinter привязываем save_settings к событию выхода
def on_closing():
    save_settings()
    root.destroy()

# В начале программы вызываем
load_settings()
root.protocol("WM_DELETE_WINDOW", on_closing)
