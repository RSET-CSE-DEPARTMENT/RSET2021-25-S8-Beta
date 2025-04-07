import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

# Server Configuration
SERVER_IP = "172.16.30.14"  # Replace with actual server IP
SERVER_PORT = 5000

class ChromeLikeAlertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Alert Receiver")
        self.root.geometry("600x350")
        self.root.overrideredirect(True)  # Hide default title bar

        # --- Custom Title Bar ---
        self.title_bar = tk.Frame(self.root, bg="#1E1E1E", relief='raised', bd=2)
        self.title_bar.pack(fill=tk.X)

        self.title_label = tk.Label(self.title_bar, text=" Alert Monitor ", bg="#1E1E1E", fg="white", font=("Arial", 10))
        self.title_label.pack(side=tk.LEFT, padx=10)

        # Minimize, Maximize, Close Buttons
        self.min_button = tk.Button(self.title_bar, text="—", command=self.minimize, bg="#1E1E1E", fg="white", bd=0)
        self.min_button.pack(side=tk.RIGHT, padx=5)

        self.max_button = tk.Button(self.title_bar, text="⬜", command=self.toggle_fullscreen, bg="#1E1E1E", fg="white", bd=0)
        self.max_button.pack(side=tk.RIGHT, padx=5)

        self.close_button = tk.Button(self.title_bar, text="✖", command=self.root.destroy, bg="#FF5F57", fg="white", bd=0)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        # Make Title Bar Draggable
        self.title_bar.bind("<B1-Motion>", self.move_window)

        # --- Main UI ---
        self.main_frame = tk.Frame(self.root, bg="#2E2E2E")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(self.main_frame, width=70, height=15, bg="#1E1E1E", fg="white", font=("Arial", 10))
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(self.main_frame, text="Start Server", command=self.start_server, bg="#4CAF50", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.stop_button = tk.Button(self.main_frame, text="Stop Server", command=self.stop_server, bg="#D32F2F", fg="white", state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Server Variables
        self.server_socket = None
        self.running = False
        self.fullscreen = False

    def start_server(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            threading.Thread(target=self.run_server, daemon=True).start()
            self.log_message("✅ Server started, waiting for alerts...")

    def run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((SERVER_IP, SERVER_PORT))

            while self.running:
                data, addr = self.server_socket.recvfrom(1024)
                alert_message = data.decode()
                self.log_message(f"🚨 ALERT: {alert_message} from {addr}")

        except Exception as e:
            self.log_message(f"⚠️ Error: {e}")

    def stop_server(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.log_message("⛔ Server stopped.")

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)

    # --- Window Controls ---
    def minimize(self):
        self.root.iconify()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes('-fullscreen', self.fullscreen)

    def move_window(self, event):
        self.root.geometry(f"+{event.x_root}+{event.y_root}")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ChromeLikeAlertApp(root)
    root.mainloop()
