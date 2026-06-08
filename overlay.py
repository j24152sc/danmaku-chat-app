import sys
import socket
import threading
import json
import random

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QWidget, QLabel

HOST = "127.0.0.1"
PORT = 5000


class Danmaku(QLabel):

    def __init__(self, text, parent):

        super().__init__(text, parent)

        self.setStyleSheet("color:white; background:transparent;")

        self.speed = random.randint(3, 8)   # 右→左スクロール速度

        self.move(
            parent.width(), # 右端から出現（右→左の弾幕）
            random.randint(0, max(0, parent.height() - 50))
        )

    def update(self):

        self.move(self.x() - self.speed, self.y())

        if self.x() + self.width() < 0:
            self.deleteLater()
            return False

        return True


class Overlay(QWidget):

    signal = pyqtSignal(str)

    def __init__(self):

        super().__init__()

        self.labels = []

        self.signal.connect(self.add)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.showFullScreen()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(16)

        threading.Thread(target=self.recv, daemon=True).start()

    def add(self, data):
        # 受信データ形式: "name||text||color||font_size"
        name, text, color, font_size = data.split("||")

        # 名前あり → 名前＋メッセージ表示 / 名前なし → メッセージのみ
        if name and name.strip() != "":
            display = f"{name} : {text}"
        else:
            display = text

        label = Danmaku(display, self)

        font_size = int(font_size)

        font = QFont("Meiryo")
        font.setPixelSize(font_size)   

        label.setFont(font)

        label.adjustSize()

     


        # 文字色対応
        label.setStyleSheet(f"color:{color}; background:transparent;")

        label.show()
        self.labels.append(label)

    def update_labels(self):

        self.labels = [l for l in self.labels if l.update()]

    def recv(self):

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

        # overlayはユーザー一覧に出ない特殊クライアント
        client.send((json.dumps({
            "type": "register",
            "name": "overlay",
            "role": "overlay"
        }) + "\n").encode())

        buffer = ""

        while True:

            data = client.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:

                line, buffer = buffer.split("\n", 1)

                if not line.strip():
                    continue

                packet = json.loads(line)

                if packet["type"] == "message":
                    
                    # デバッグ用受信確認（パケット全体） 
                    print("Overlay受信:", packet)

                    name = packet.get("name", "")
                    text = packet.get("text", "")
                    color = packet.get("color", "#ffffff")
                    font_size = int(packet.get("font_size", 20))
                    
                    # デバッグ用受信確認（フォントサイズ）)
                    print("font_size受信:", font_size)

                    # 送信データをUIへ渡す（name/text/color/font_size）
                    self.signal.emit(
                        f"{name}||{text}||{color}||{font_size}"
                    )

                # ユーザー一覧受信（表示用途ではないデバッグ）
                elif packet["type"] == "users":
                    print("オンライン:", packet["users"])



if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = Overlay()
    sys.exit(app.exec())

