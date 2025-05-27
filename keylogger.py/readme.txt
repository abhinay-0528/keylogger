===============================
🛡️ Educational Keylogger Project
===============================

🔍 DESCRIPTION:
----------------
This is an educational keystroke logging project built using Python and Flask.
It demonstrates concepts like:
- Keyboard input capture
- Real-time web interface
- Data encryption (Fernet)
- Secure log download and decryption

⚠️ LEGAL & ETHICAL NOTICE:
--------------------------
This tool is for **educational purposes only**. Unauthorized use of keyloggers is illegal and unethical.
Use this project **only** on machines you own or with **explicit permission**. Misuse may violate computer fraud and privacy laws.

📦 FEATURES:
------------
- Logs keystrokes in the background
- Encrypts logs using Fernet symmetric encryption
- UI to start/stop logging, encrypt, decrypt, and download logs
- Real-time status updates and ripple button effects
- Secure download of encrypted logs and keys
- Password-only logging supported

🛠️ PROJECT STRUCTURE:
----------------------
| File / Folder       | Purpose                                      |
|---------------------|----------------------------------------------|
| app.py              | Flask server with routes for control/UI      |
| keylogger.py        | Background keylogging with encryption        |
| key_log             | File that stores encrypted keystrokes        |
| key.key             | Fernet encryption key (auto-generated)       |
| templates/          | HTML templates for Flask                     |
| static/             | CSS and assets                               |
| logs.html           | Displays decrypted log output                |
| README.txt          | This documentation                           |

🚀 SETUP & USAGE:
-------------------
1. **Install dependencies**:
pip install pynput cryptography

2. **Run the Flask app**:
python app.py

3. **Access the Web UI**:
Open `http://127.0.0.1:5000` in your browser.

4. **Start Logging**:
- Click "▶️ Start Logging"
- Your keystrokes will be recorded

5. **Encrypt Logs**:
- Click "🔐 Encrypt Data" to encrypt captured keys

6. **Download Logs/Key**:
- Click 📥 to download log and encryption key securely

7. **Decrypt Logs**:
- Click "Decrypt Log" to view decrypted content

📁 NOTE:
---------
- `key_log` and `key.key` will be auto-generated
- Decryption works only if logs were encrypted using the saved key
- Only the password or relevant string should be stored in `key_log`

👨‍💻 AUTHOR:
-------------
This project was built for a cybersecurity ethical hacking course as a learning tool. For contributions or feedback, open an issue or PR on the GitHub repo.

📚 DISCLAIMER:
---------------
This tool is not intended for illegal surveillance. All use cases must comply with local laws and ethical guidelines. The author is not responsible for misuse.

