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
        self.setFont(QFont("Meiryo", 20))
        self.adjustSize()

        self.speed = random.randint(3, 8)

        self.move(
            parent.width(),
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
        name, text, color = data.split("||")

        label = Danmaku(f"{name} : {text}", self)
        label.setStyleSheet(f"color:{color}; background:transparent;")

        label.show()
        self.labels.append(label)

    def update_labels(self):

        self.labels = [l for l in self.labels if l.update()]

    def recv(self):

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST, PORT))

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

                    name = packet.get("name", "")
                    text = packet.get("text", "")
                    color = packet.get("color", "#ffffff")

                    self.signal.emit(f"{name}||{text}||{color}")

                elif packet["type"] == "users":
                    print("オンライン:", packet["users"])



if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = Overlay()
    sys.exit(app.exec())