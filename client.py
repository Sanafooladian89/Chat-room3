import socket
import threading
import time

HOST = "127.0.0.1"
PORT = 8080


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

    client.connect((HOST, PORT))

    print("Connected to server!")

    username = input("Enter your username: ")
    client.send(username.encode())

    def receive_messages():
      while True:
        try:
           message = client.recv(1024).decode()

           if not message:
             break
        
           print(message)

        except OSError:
         break
      
    receive_thread = threading.Thread(
    target=receive_messages
)
    receive_thread.start()

    # while True:
        
    #     message = input("Message: ")
    #     receiver = input(
    #     """If the message is not public,
    #       enter the name of the intended recipient; otherwise, press Enter. """
    # ).strip()
    #     current_time = time.strftime("%H:%M:%S")
        
    #     if receiver == "":
    #       msg = f"PUBLIC|{username}||{message}|{current_time}"
    #     else:
    #       msg = f"PRIVATE|{username}|{receiver}|{message}|{current_time}"
        
    #     client.send(msg.encode())
    
    # Hajzade edit:
    while True:
        try:
            message = input()
            if not message:
                continue
            if message.lower() == "exit":
                client.send("exit".encode())
                break
            if message.lower() == "users":
                client.send("users".encode())
                continue

            current_time = time.strftime("%H:%M:%S")

            # اگر با @ شروع شد یعنی خصوصی است: مثلا @sara salam
            if message.startswith("@"):
                parts = message.split(" ", 1)
                receiver = parts[0][1:]  # حذف علامت @
                text = parts[1] if len(parts) > 1 else ""
                msg = f"PRIVATE|{username}|{receiver}|{text}|{current_time}"
            else:
                msg = f"PUBLIC|{username}||{message}|{current_time}"

            client.send(msg.encode())
        except (KeyboardInterrupt, EOFError):
            break
