import subprocess
import sys
import os
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

client_path = os.path.join(BASE_DIR, "client_sender.py")
overlay_path = os.path.join(BASE_DIR, "overlay.py")

client_process = None
overlay_process = None


def start_all():

    global client_process, overlay_process

    if client_process is None:
        client_process = subprocess.Popen([sys.executable, client_path])

    if overlay_process is None:
        overlay_process = subprocess.Popen([sys.executable, overlay_path])

    status_label.config(text="● RUNNING", fg="#00ff88")


def stop_all():

    global client_process, overlay_process

    if client_process:
        client_process.terminate()
        client_process = None

    if overlay_process:
        overlay_process.terminate()
        overlay_process = None

    status_label.config(text="● STOPPED", fg="#ff4444")


def restart():
    stop_all()
    root.after(500, start_all)


root = tk.Tk()
root.title("Danmaku Control Panel")
root.geometry("360x240")
root.configure(bg="#1e1e1e")


title = tk.Label(
    root,
    text="DANMAKU SYSTEM",
    font=("Arial", 16, "bold"),
    fg="white",
    bg="#1e1e1e"
)
title.pack(pady=10)


status_label = tk.Label(
    root,
    text="● STOPPED",
    font=("Arial", 12),
    fg="#ff4444",
    bg="#1e1e1e"
)
status_label.pack(pady=5)


btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack(pady=20)


start_btn = tk.Button(
    btn_frame,
    text="▶ START",
    width=12,
    bg="#2d2d2d",
    fg="white",
    activebackground="#00aa66",
    command=start_all
)
start_btn.grid(row=0, column=0, padx=5)


stop_btn = tk.Button(
    btn_frame,
    text="■ STOP",
    width=12,
    bg="#2d2d2d",
    fg="white",
    activebackground="#aa0000",
    command=stop_all
)
stop_btn.grid(row=0, column=1, padx=5)


restart_btn = tk.Button(
    root,
    text="↻ RESTART",
    width=25,
    bg="#333333",
    fg="white",
    command=restart
)
restart_btn.pack(pady=10)

root.mainloop()