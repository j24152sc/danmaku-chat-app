import socket
import json
import threading
import tkinter as tk

HOST = "127.0.0.1"
PORT = 5000

client = None
target_vars = {}

def on_enter(event):
    send_message()
    return "break"

def connect_server():

    global client

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    name = name_entry.get().strip()

    # 空ならそのまま送る（サーバーでゲスト化）
    register = {
        "type": "register",
        "name": name
    }

    client.send((json.dumps(register) + "\n").encode("utf-8"))

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
                    users = packet["users"]
                    
                    # client_senderはUIに出さない
                    users = [u for u in users if u != "guest_sender"]

                    update_users(users)
        except:
            pass


def update_users(users):

    for w in user_frame.winfo_children():
        w.destroy()

    tk.Label(user_frame, text="オンラインユーザー").pack(anchor="w")
    
    if "all" not in users and len(users) > 0:
        users = ["all"] + users


    target_vars.clear()

    for u in users:

        var = tk.BooleanVar()

        tk.Checkbutton(
            user_frame,
            text=u,
            variable=var
        ).pack(anchor="w")

        target_vars[u] = var


def send_message():

    if client is None:
        return

    name = name_entry.get().strip()
    text = message_entry.get().strip()
    

    if text == "":
        return

    targets = [u for u, v in target_vars.items() if v.get() and u != "all"]
    
    if len(targets) == 0:
        return
    
    if len(targets) == 0:
        targets = ["all"]

    packet = {
        "type": "message",
        "name": name,
        "text": text,
        "color": color_var.get(),
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
message_entry.bind("<Return>", on_enter)

# =========================
# ニコニコ風カラー選択
# =========================

color_var = tk.StringVar(value="#ffffff")

tk.Label(root, text="文字色（ニコニコ風）").pack()

color_frame = tk.Frame(root)
color_frame.pack()

colors = {
    "白": "#ffffff",
    "赤": "#ff2d2d",
    "ピンク": "#ff66cc",
    "オレンジ": "#ff9900",
    "黄": "#ffd400",
    "緑": "#33cc66",
    "水色": "#00ccff",
    "青": "#3366ff",
    "紫": "#9933ff"
}

for name, code in colors.items():

    tk.Radiobutton(
        color_frame,
        text=name,
        value=code,
        variable=color_var
    ).pack(side="left")


user_frame = tk.Frame(root)
user_frame.pack(fill="both", expand=True)

tk.Button(root, text="接続", command=connect_server).pack()
tk.Button(root, text="送信", command=send_message).pack()
tk.Label(
    root,
    text="Enterでも送信OK",
    fg="gray"
).pack()

root.mainloop()