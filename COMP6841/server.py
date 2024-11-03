from flask import Flask, request, jsonify
from cryptography.fernet import Fernet
import base64
import json
import os

app = Flask(__name__)

# Load or generate the encryption key
def load_key():
    key_path = "hidden.key"
    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
    else:
        with open(key_path, "rb") as key_file:
            key = key_file.read()
    return key

key = load_key()
cipher = Fernet(key)

# Decrypt Base64-encoded encrypted data
def decrypt_data(encrypted_data_base64):
    encrypted_data = base64.b64decode(encrypted_data_base64)  # Decode Base64 to binary
    decrypted_data = cipher.decrypt(encrypted_data)  # Decrypt binary data
    return json.loads(decrypted_data)  # Convert JSON string back to dictionary

@app.route('/receive-data', methods=['POST'])
def receive_data():
    try:
        encrypted_data_base64 = request.json.get("encrypted_data")
        data = decrypt_data(encrypted_data_base64)

        # Log data to file
        with open("received_data.txt", "a") as f:
            f.write(str(data) + "\n")
        return jsonify({"message": "Data received successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to decrypt or process data: {e}"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
