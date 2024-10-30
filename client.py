import threading
import socket

BUFFER_SIZE = 4096

def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        return True
    return False

def is_valid_port(port):
    return port.isdigit() and 1024 <= int(port) <= 65535

def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            print(message.decode())
        except:
            print("Disconnected from server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        server_ip = input("Enter server IP: ")
        server_port = input("Enter server port: ")
        
        if is_valid_ip(server_ip) and is_valid_port(server_port):
            server_address = (server_ip, int(server_port))
            break
        else:
            print("Invalid IP or port. Please try again.")

    while True:
        username = input("Enter username: ")
        client_socket.sendto(f"USERNAME:{username}".encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        response_message = response.decode()
        print(response_message)
        
        if response_message == "Username accepted.":
            break

    while True:
        password = input("Enter password: ")
        client_socket.sendto(f"PASSWORD:{password}".encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        response_message = response.decode()
        print(response_message)

        if response_message == "Password accepted. You are connected.":
            break

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