import threading
import socket

SERVER_PASSWORD = "123"

def handle_client(server_socket, client_address, clients):
    while True:
        try:
            message, address = server_socket.recvfrom(4096)
            decoded_message = message.decode()
            print(f"Message from {address}: {decoded_message}")
            broadcast(server_socket, message, address, clients)
        except:
            print(f"Client {client_address} disconnected.")
            if client_address in clients:
                del clients[client_address]
            break

def broadcast(server_socket, message, source_address, clients):
    for address in clients:
        if address != source_address:
            server_socket.sendto(message, address)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("localhost", 2305))
    print("Server is running on port 2305")

    clients = {}

    while True:
        message, client_address = server_socket.recvfrom(4096)
        decoded_message = message.decode()

        if client_address in clients:
            print(f"Message from {client_address}: {decoded_message}")
            broadcast(server_socket, message, client_address, clients)
            continue
        
        if decoded_message == SERVER_PASSWORD:
            clients[client_address] = True
            print(f"Client {client_address} connected.")
            server_socket.sendto("Password accepted. You are connected.".encode(), client_address)
        else:
            print(f"Client {client_address} provided invalid password.")
            server_socket.sendto("Invalid password. Please try again.".encode(), client_address)

if __name__ == "__main__":
    main()