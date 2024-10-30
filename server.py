import socket

SERVER_IP = "192.168.29.1"
SERVER_PORT = 9999
SERVER_PASSWORD = "123"
BUFFER_SIZE = 4096

def broadcast(server_socket, message, source_address, clients):
    for address in clients:
        if address != source_address:
            server_socket.sendto(message, address)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server is running on {SERVER_IP}:{SERVER_PORT}")

    clients = {}
    usernames = {}

    while True:
        message, client_address = server_socket.recvfrom(BUFFER_SIZE)
        decoded_message = message.decode()

        if decoded_message.startswith("USERNAME:"):
            username = decoded_message.split(":", 1)[1]
            if username in usernames.values():
                server_socket.sendto("Username already taken. Please choose a different one.".encode(), client_address)
            else:
                usernames[client_address] = username
                server_socket.sendto("Username accepted.".encode(), client_address)
            continue

        elif decoded_message.startswith("PASSWORD:"):
            password = decoded_message.split(":", 1)[1]
            if password == SERVER_PASSWORD:
                clients[client_address] = True
                print(f"Client {client_address} connected with username '{usernames[client_address]}'.")
                server_socket.sendto("Password accepted. You are connected.".encode(), client_address)
            else:
                server_socket.sendto("Invalid password. Please try again.".encode(), client_address)
            continue

        if client_address in clients:
            print(f"Message from {client_address} {decoded_message}")
            broadcast(server_socket, message, client_address, clients)

if __name__ == "__main__":
    main()