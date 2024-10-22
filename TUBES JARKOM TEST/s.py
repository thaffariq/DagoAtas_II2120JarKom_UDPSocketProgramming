import socket
import threading

# Hardcoded server password
SERVER_PASSWORD = "1234"

clients = []  # List untuk menyimpan alamat client yang terhubung

# Fungsi untuk menangani pesan dari klien
def handle_client(client_socket, client_address):
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            decoded_message = message.decode()

            # Memeriksa apakah pesan adalah password dari klien
            if decoded_message.startswith("PASSWORD:"):
                client_password = decoded_message.split(":")[1]

                if client_password == SERVER_PASSWORD:
                    client_socket.sendto("PASSWORD_ACCEPTED".encode(), client_address)
                    if client_address not in clients:
                        clients.append(client_address)  # Menambahkan client ke daftar
                else:
                    client_socket.sendto("PASSWORD_REJECTED".encode(), client_address)

            # Jika bukan password, broadcast pesan ke klien lain
            else:
                print(f"{decoded_message}")  # Log pesan ke server
                broadcast(decoded_message, client_socket, client_address)

        except:
            print(f"Client {client_address} disconnected.")
            if client_address in clients:
                clients.remove(client_address)
            break

# Fungsi untuk mengirim pesan ke semua klien kecuali pengirimnya
def broadcast(message, client_socket, sender_address):
    for client in clients:
        if client != sender_address:  # Jangan kirim balik ke pengirim
            try:
                client_socket.sendto(message.encode(), client)
            except:
                client_socket.close()
                clients.remove(client)

# Fungsi utama untuk server
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("localhost", 2305)
    server_socket.bind(server_address)

    print("Server is running and waiting for clients...")

    while True:
        # Mendengarkan pesan dari klien
        message, client_address = server_socket.recvfrom(1024)

        if client_address not in clients:
            print(f"New connection from {client_address}")
            clients.append(client_address)

        # Memulai thread untuk menangani client
        client_thread = threading.Thread(target=handle_client, args=(server_socket, client_address))
        client_thread.daemon = True
        client_thread.start()

if __name__ == "__main__":
    main()
