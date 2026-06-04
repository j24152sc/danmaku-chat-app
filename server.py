import socket
import threading
import json

HOST = "0.0.0.0"
PORT = 5000

clients = {}  # conn -> name
guest_count = 0


def broadcast(data):

    msg = (json.dumps(data) + "\n").encode("utf-8")

    for c in list(clients.keys()):
        try:
            c.send(msg)
        except:
            try:
                del clients[c]
            except:
                pass


def send_user_list():

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
            "users": ["all"] + users
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

                if packet["type"] == "register":

                    name = packet.get("name", "").strip()
                    role = packet.get("role", "user")
                    
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

                elif packet["type"] == "message":

                    msg = {
                        "type": "message",
                        "name": packet.get("name", ""),
                        "text": packet.get("text", ""),
                        "to": packet.get("to", ["all"])
                    }

                    broadcast(msg)

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