import threading
import socket

def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(f"{message.decode()}")
        except:
            print(f"Disconnected from server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (("localhost", 2305))

    username = input("Enter username : ")
    password = input("Enter password : ")
    client_socket.sendto(f"{username} has joined.".encode(), server_address)

    threading.Thread(target=recv_messages, args=(client_socket,)).start()

    while True:
        message = input()
        if(message.lower() == "exit"):
            print("left from chatroom...")
            break

        complete_message = (f"{username} : {message}")
        client_socket.sendto(complete_message.encode(), server_address)

if(__name__ == "__main__"):
    main()
