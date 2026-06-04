✔ server
1つだけ起動（絶対）
✔ client
送る人だけ起動
✔ overlay
見たい人は全員起動

PC1：server.py（絶対これだけ）
PC2：client_sender.py + overlay.py
PC3：client_sender.py + overlay.py
そうしないと役割が集中していて構造が分かりにくく不安定。

◯「ソケット通信を用いたリアルタイム弾幕チャットシステム」コミットが元
◯allはサーバーが先頭に必ず入れる