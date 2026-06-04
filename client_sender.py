import socket
import json
import threading
import tkinter as tk

HOST = "127.0.0.1"
PORT = 5000

client = None
target_vars = {}


def connect_server():

    global client

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    name = name_entry.get().strip()

    client.send((json.dumps({
        "type": "register",
        "name": name
    }) + "\n").encode("utf-8"))

    threading.Thread(target=receive_loop, daemon=True).start()


def receive_loop():

    buffer = ""

    while True:

        try:
            data = client.recv(4096).decode("utf-8")
            buffer += data

            while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                packet = json.loads(line)

                if packet["type"] == "users":
                    update_users(packet["users"])

        except:
            pass


def update_users(users):

    for w in user_frame.winfo_children():
        w.destroy()

    tk.Label(user_frame, text="オンラインユーザー").pack(anchor="w")

    target_vars.clear()

    for u in users:

        var = tk.BooleanVar()

        tk.Checkbutton(
            user_frame,
            text=u,
            variable=var
        ).pack(anchor="w")

        target_vars[u] = var


def send_message(event=None):

    if client is None:
        return

    name = name_entry.get().strip()
    text = message_entry.get().strip()

    if text == "":
        return

    targets = [u for u, v in target_vars.items() if v.get()]

    if not targets:
        targets = ["all"]

    packet = {
        "type": "message",
        "name": name,
        "text": text,
        "to": targets
    }

    client.send((json.dumps(packet) + "\n").encode("utf-8"))

    message_entry.delete(0, tk.END)


root = tk.Tk()
root.title("Danmaku Sender")
root.geometry("500x400")

tk.Label(root, text="名前（空OK）").pack()

name_entry = tk.Entry(root)
name_entry.pack(fill="x")

tk.Label(root, text="メッセージ").pack()

message_entry = tk.Entry(root)
message_entry.pack(fill="x")

user_frame = tk.Frame(root)
user_frame.pack(fill="both", expand=True)

tk.Button(root, text="接続", command=connect_server).pack()
tk.Button(root, text="送信", command=send_message).pack()

root.mainloop()