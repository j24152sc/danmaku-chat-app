import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

clients = {}  # conn -> name
guest_count = 0 # 名前未設定ユーザーのゲスト番号管理


def broadcast(data):
    # 全員にJSONを送る関数
    msg = (json.dumps(data) + "\n").encode("utf-8")

    for c in list(clients.keys()):
        try:
            c.send(msg)
        except:
            try:
                del clients[c]
            except:
                pass

# オンラインユーザー一覧を送る
def send_user_list():

    # overlayをユーザー一覧から除外
    users = [
        v["name"]
        for v in clients.values()
        if v["role"] != "overlay"
    ]
    
    # overlayや空だけなら除外済み

    if len(users) == 0:
        data = {
            "type": "users",
            "users": []
        }
    else:
        data = {
            "type": "users",
            "users": ["all"] + users    # 全体送信用
        }


    broadcast(data)


def handle_client(conn):

    global guest_count

    buffer = ""

    try:
        while True:

            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode("utf-8")

            while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                packet = json.loads(line)

                # 登録処理
                if packet["type"] == "register":

                    name = packet.get("name", "").strip()
                    role = packet.get("role", "user")   # overlay判定用
                    
                    # overlayは名前固定
                    if role == "overlay" or name == "overlay":
                        name = "overlay"
                        role = "overlay"
                    # 空ならゲスト化（senderだけ）
                    if name == "":
                        guest_count += 1
                        name = f"ゲスト{guest_count}"
                    
                    clients[conn] = {
                        "name": name,
                        "role": role
                    }
                    
                    send_user_list()
                    
                # メッセージ処理
                elif packet["type"] == "message":
                    # クライアントから送られた名前（空なら後でゲストになることもある）
                    name = packet.get("name", "").strip()
                    # メッセージ本文
                    text = packet.get("text", "")
                    # 文字色（指定がなければ白）
                    color = packet.get("color", "#ffffff")
                    # 送信対象リスト（例: ["all"] や ["A", "B"]）
                    targets = packet.get("to", ["all"]) 
                    # font_size受け取る
                    font_size = packet.get("font_size", 20)

                    # 送信用データ
                    msg = {
                        "type": "message",
                        "name": name,
                        "text": text,
                        "color": color,
                        "font_size": font_size,
                        "to": targets
                    }
                    
                    #送信元（自分）を保存:自分に送らないために使う
                    sender_conn = conn

                    # all → 全員（自分除外）に送る
                    if "all" in targets:

                        # 接続中の全ユーザーをループ
                        for c in list(clients.keys()):
                            if c == sender_conn:
                                continue

                            try:
                                c.send((json.dumps(msg) + "\n").encode("utf-8"))
                            # 送信失敗してもサーバー止めない
                            except:
                                pass

                    # 個別送信
                    else:
                        # 接続ユーザー全員チェック
                        for c, info in list(clients.items()):
                            if info["name"] in targets and c != sender_conn:
                                try:
                                    #対象ユーザーだけに送信
                                    c.send((json.dumps(msg) + "\n").encode("utf-8"))
                                except:
                                    pass

    except:
        pass

    finally:

        if conn in clients:
            if conn in clients:
                del clients[conn]

        conn.close()
        send_user_list()


def main():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server Start {HOST}:{PORT}")

    while True:

        conn, addr = server.accept()
        print("Connect:", addr)

        threading.Thread(
            target=handle_client,
            args=(conn,),
            daemon=True
        ).start()


if __name__ == "__main__":
    main()