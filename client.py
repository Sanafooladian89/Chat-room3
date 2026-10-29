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

    while True:
        
        message = input("Message: ")
        receiver = input(
        """If the message is not public,
          enter the name of the intended recipient; otherwise, press Enter. """
    ).strip()
        current_time = time.strftime("%H:%M:%S")
        
        if receiver == "":
          msg = f"PUBLIC|{username}||{message}|{current_time}"
        else:
          msg = f"PRIVATE|{username}|{receiver}|{message}|{current_time}"
        
        client.send(msg.encode())

