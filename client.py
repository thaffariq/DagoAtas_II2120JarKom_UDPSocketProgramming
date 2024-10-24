import threading
import socket

def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(4096)
            print(message.decode())
        except:
            print("Disconnected from server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("localhost", 2305)

    username = input("Enter username: ")

    while True:
        password = input("Enter password: ")
        client_socket.sendto(password.encode(), server_address)
        
        response, _ = client_socket.recvfrom(4096)
        response_message = response.decode()
        print(response_message)

        if response_message == "Password accepted. You are connected.":
            break

    client_socket.sendto(f"{username} has joined.".encode(), server_address)

    threading.Thread(target=recv_messages, args=(client_socket,)).start()

    while True:
        message = input()
        if message.lower() == "exit":
            print("You have left the chatroom.")
            break

        complete_message = f"{username}: {message}"
        client_socket.sendto(complete_message.encode(), server_address)

if __name__ == "__main__":
    main()