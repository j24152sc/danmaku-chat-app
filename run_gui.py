import subprocess
import tkinter as tk

processes = []


def start_app():

    global processes

    if processes:
        return

    processes.append(
        subprocess.Popen(["python", "server.py"])
    )

    processes.append(
        subprocess.Popen(["python", "overlay.py"])
    )

    processes.append(
        subprocess.Popen(["python", "client_sender.py"])
    )

    status_label.config(text="起動中")


def stop_app():

    global processes

    for p in processes:
        p.terminate()

    processes = []

    status_label.config(text="停止中")


root = tk.Tk()
root.title("Danmaku Launcher")
root.geometry("300x200")


title = tk.Label(
    root,
    text="Danmaku Control Panel",
    font=("Arial", 14)
)
title.pack(pady=10)


start_btn = tk.Button(
    root,
    text="▶ 起動",
    width=20,
    command=start_app
)
start_btn.pack(pady=5)


stop_btn = tk.Button(
    root,
    text="■ 停止",
    width=20,
    command=stop_app
)
stop_btn.pack(pady=5)


status_label = tk.Label(
    root,
    text="停止中",
    fg="gray"
)
status_label.pack(pady=10)


root.mainloop()