import socket
import json
import threading
import tkinter as tk

HOST = "127.0.0.1"
PORT = 5000

client = None
target_vars = {}

def on_enter(event):    # Enterキー送信対応
    send_message()
    return "break"

def connect_server():

    global client

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    name = name_entry.get().strip()
    
    # サーバーと同期用に保持
    self_name = name

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
                    
                # メッセージ受信
                elif packet["type"] == "message":

                    print("自分に届いた:", packet)
        except:
            pass

# サーバーから受信したユーザー一覧（overlay除外済み）
# client_sender自身はユーザーとして表示されない設計
def update_users(users):

    # 現在のチェック状態を保存（ここ重要）
    existing = {k: v.get() for k, v in target_vars.items()}

    for w in user_frame.winfo_children():
        w.destroy()

    tk.Label(user_frame, text="オンラインユーザー").pack(anchor="w")

    # target_varsをリセット
    target_vars.clear()

    for u in users:

        var = tk.BooleanVar()
        
        def on_toggle(user=u, v=var):
            # allを押したとき
            if user == "all" and v.get():
                for k, v2 in target_vars.items():
                    if k != "all":
                        v2.set(False)

            # 他を押したとき
            elif user != "all" and v.get():
                if "all" in target_vars:
                    target_vars["all"].set(False)
                    
        cb = tk.Checkbutton(
            user_frame,
            text=u,
            variable=var,
            command=on_toggle
        )
        cb.pack(anchor="w")

        target_vars[u] = var

    

        # 前回の選択状態を復元
        if u in existing:
            var.set(existing[u])

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

    # デバッグ用選択確認(小／中／大ボタンの選択確認)
    print("選択中:", font_size_var.get())
    print("選択:", font_size_var.get())
    print("辞書:", font_sizes)
    print("変換:", font_sizes[font_size_var.get()])
    
    # チェックが入っているユーザーをすべて取得する
    targets = [u for u, v in target_vars.items() if v.get()]
    
    # デバッグ用選択確認（送信）
    print("送信targets:", targets)
    print("name:", name)
    
    # 送信時だけ all 判定
    if "all" in targets:
        targets = ["all"]
    
    # 何も選ばれていない場合は送信しない
    if len(targets) == 0:
        return

    # 送信データ
    packet = {
        "type": "message",
        "name": name,
        "text": text,
        "color": color_var.get(),
        "font_size": font_sizes[font_size_var.get()],# 表示用（小・中・大）を数値（20/28/36）に変換して送信
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
message_entry.bind("<Return>", on_enter)    # Enterキー送信対応


# ニコニコ風カラー選択

color_var = tk.StringVar(value="#ffffff")   # 文字色（ニコニコ風カラー）

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

# フォントサイズ選択（小・中・大）

font_size_var = tk.StringVar(value="小")  # デフォルトは小（現在のサイズ）

tk.Label(root, text="フォントサイズ").pack()

font_frame = tk.Frame(root)
font_frame.pack()

font_sizes = {
    "小": 40,  
    "中": 80,
    "大": 120,
}

for name, size in font_sizes.items():

    tk.Radiobutton(
        font_frame,
        text=name,  # # 表示（小・中・大）
        value=name, # 「小・中・大」を送るようにする(キー送る)
        variable=font_size_var
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