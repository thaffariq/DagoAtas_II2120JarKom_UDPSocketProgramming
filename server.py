import threading
import socket

def handle_client(server_socket, client_address, client):
    while True:
        try:
            message, address = server_socket.recvfrom(1024)
            print(f"Message from {address} : {message.decode()}")
            broadcast(server_socket, message, address, client)
                
        except:
            print(f"client {client_address} disconnected.")
            if(client_address) in (client):
                del client[client_address]
            break

def broadcast(server_socket, message, address_source, client):
    for(address) in (client):
        if(address != address_source):
            server_socket.sendto(message, address)

def main():
    server_socket= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("localhost", 2305))
    print("server is running in port 2305")

    client = {}

    while True:
        message, client_address = server_socket.recvfrom(1024)
        if(client_address) not in (client):
            client[client_address] = True
            print(f"Client {client_address} is connected.")
        
        threading.Thread(target=handle_client, args=(server_socket, client_address, client)).start()

if(__name__ == "__main__"):
    main()