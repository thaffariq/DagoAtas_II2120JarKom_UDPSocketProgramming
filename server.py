import threading
import socket

def handle_client(server_socket, client_address, clients):
    while True:
        try:
            message, address = server_socket.recvfrom(1024)
            print(f"Message from {address} : {message.decode()}")
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
        message, client_address = server_socket.recvfrom(1024)
        if client_address not in clients:
            clients[client_address] = True
            print(f"Client {client_address} connected.")
        
        threading.Thread(target=handle_client, args=(server_socket, client_address, clients)).start()

if __name__ == "__main__":
    main()