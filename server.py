import socket

# Menentukan alamat IP dan port server
SERVER_IP = "192.168.158.227"
SERVER_PORT = 9999
SERVER_PASSWORD = "123"
BUFFER_SIZE = 4096

# Fungsi untuk mengirim pesan ke semua klien yang terhubung kecuali pengirim
def broadcast(server_socket, message, source_address, clients):
    for address in clients:
        if address != source_address:
            server_socket.sendto(message, address)

def main():
    # Membuat socket UDP untuk server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))  # Mengikat socket ke IP dan port
    print(f"Server berjalan di {SERVER_IP}:{SERVER_PORT}")

    clients = {}     # Dictionary untuk menyimpan klien yang terhubung
    usernames = {}   # Dictionary untuk menyimpan username dari klien

    while True:
        # Menerima pesan dari klien mana pun
        message, client_address = server_socket.recvfrom(BUFFER_SIZE)
        decoded_message = message.decode()

        # Memeriksa apakah pesan berisi username dan memprosesnya
        if decoded_message.startswith("USERNAME:"):
            username = decoded_message.split(":", 1)[1]
            if username in usernames.values():
                server_socket.sendto("Username sudah dipakai. Silakan pilih username lain.".encode(), client_address)
            else:
                usernames[client_address] = username
                server_socket.sendto("Username diterima.".encode(), client_address)
            continue

        # Memeriksa apakah pesan berisi password dan memverifikasinya
        elif decoded_message.startswith("PASSWORD:"):
            password = decoded_message.split(":", 1)[1]
            if password == SERVER_PASSWORD:
                clients[client_address] = True  # Menandai klien sebagai terhubung
                print(f"Klien {client_address} terhubung dengan username '{usernames[client_address]}'.")
                server_socket.sendto("Password diterima. Anda terhubung.".encode(), client_address)
            else:
                server_socket.sendto("Password salah. Silakan coba lagi.".encode(), client_address)
            continue

        # Jika klien terhubung, kirimkan pesan mereka ke klien lainnya
        if client_address in clients:
            print(f"Pesan dari {client_address} {decoded_message}")
            broadcast(server_socket, message, client_address, clients)

if __name__ == "__main__":
    main()