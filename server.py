# سلام عزیزم چت روم شما بررسی شد.
# تشکر میکنم بابت این که تقریبا 
# اکثر مواردی که گفته شده انجام شده.
# مواردی که باید اصلاح بشه:
# 1. وقتی کاربر پیامی میفرسته باید کنار پیامش اسمش نوشته بشه 
# چون همه دارن میبینن و باید بدونن کدوم پیام برای کی هست.
# 2. زمان پیام ثبت میشه اما تو سرور نمایش داده میشه بهتره 
# این زمان رو تو کلاینت نمایش بدین چون نمایشش تو سرور بی فایده هست.
# 3. یکی درمیون موقع فرستادن پیام کلاینت اینطوری پیام رو ازمون میخواد
# Message:
# [تو بعدی اینو نمیگه و خالیه]
# بهتره هر سری message رو بگه.


import socket
import threading
from database_manager import ChatDatabase

HOST = "127.0.0.1"
PORT = 8080

clients = []
users = []
user_sessions = []

db = ChatDatabase()

def broadcast(msg, skip=None):
    dead = []
    for client in clients:
        if client is skip:
            continue
        try:
            client.send(msg.encode())
        except OSError:
            dead.append(client)

    for client in dead:
        if client in clients:
            clients.remove(client)

def cleanup(conn, username):
    if username in users:
        users.remove(username)
    if conn in clients:
        clients.remove(conn)
    for session in user_sessions[:]:
        if session[1] is conn:
            user_sessions.remove(session)
            break

def receive_messages(conn, username):
    while True:
        try:
            raw_data = conn.recv(1024)
        except OSError:
            break

        if not raw_data:
            break

        try:
            raw_message = raw_data.decode()
        except UnicodeDecodeError:
            continue

        if not raw_message or raw_message == "exit":
            break

        if raw_message == "users":
            conn.send(", ".join(users).encode())
            continue

        parts = raw_message.split("|")

        if len(parts) < 5:
            print(f"[WARN] Bad format from {username}: {raw_message}")
            continue

        msg_type = parts[0]
        sender_name = parts[1]
        receiver_name = parts[2]
        message_text = parts[3]
        timestamp = parts[4]

        try:
            if msg_type == "PUBLIC":
                db.save_message(sender=username, message=message_text, receiver=None)
                broadcast(f"[{timestamp}] {username}: {message_text}")

            elif msg_type == "PRIVATE":
                if receiver_name not in users:
                    conn.send(f"[Server] {receiver_name} is not online.".encode())
                    continue

                db.save_message(sender=username, message=message_text, receiver=receiver_name)

                receiver_conn = None
                for session in user_sessions:
                    if session[0] == receiver_name:
                        receiver_conn = session[1]
                        break

                if receiver_conn:
                    try:
                        receiver_conn.send(
                            f"[Private from {username}] [{timestamp}]: {message_text}".encode()
                        )
                    except OSError:
                        pass

                conn.send(
                    f"[Private to {receiver_name}] [{timestamp}]: {message_text}".encode()
                )

        except Exception as e:
            print(f"[ERROR] handling message from {username}: {e}")

    cleanup(conn, username)
    broadcast(f"{username} left the chat", skip=conn)
    conn.close()

def handle_client(conn, addr):
    try:
        print("Connection from:", addr)
        clients.append(conn)

        username_bytes = conn.recv(1024)
        if not username_bytes:
            return
        username = username_bytes.decode().strip()

        if not username:
            username = "Unknown"

        print("Username:", username)
        users.append(username)
        user_sessions.append([username, conn])

        #  فقط تاریخچه مجاز برای همین کاربر
        recent_msgs = db.get_messages_for_user(username)
        for sender, msg, receiver, timestamp in recent_msgs:
            if receiver is None:
                conn.send(f"[{timestamp}] {sender}: {msg}".encode())
            elif sender == username:
                conn.send(f"[{timestamp}] [Private to {receiver}]: {msg}".encode())
            else:
                conn.send(f"[{timestamp}] [Private from {sender}]: {msg}".encode())

        join_message = f"{username} joined the chat"
        print(join_message)
        broadcast(join_message, skip=conn)

        receive_thread = threading.Thread(
            target=receive_messages,
            args=(conn, username),
            daemon=True
        )
        receive_thread.start()

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server is running on {HOST}:{PORT}")

    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
        except KeyboardInterrupt:
            print("\nServer stopping...")
            break
        except Exception as e:
            print(f"Error accepting connection: {e}")
