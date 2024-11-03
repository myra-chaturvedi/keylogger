import pyperclip
import time

last_clipboard = ""

def log_clipboard():
    global last_clipboard
    try:
        clipboard_content = pyperclip.paste()
        # Check if clipboard content has changed and is non-empty
        if clipboard_content != last_clipboard and clipboard_content.strip() != "":
            print(f"Clipboard captured: {clipboard_content}")  # Debugging print
            with open("clipboard.txt", "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Clipboard: {clipboard_content}\n")
            last_clipboard = clipboard_content  # Update last content
    except Exception as e:
        print(f"Clipboard logging error: {e}")

# Continuous monitoring loop
print("Starting clipboard monitoring. Copy some text to the clipboard...")

while True:
    log_clipboard()  # Call the function to check clipboard content
    time.sleep(5)    # Check every 5 seconds
