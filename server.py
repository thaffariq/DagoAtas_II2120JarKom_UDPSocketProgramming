# Server RC4 dengan IP dinamis
import socket
import threading

# Menentukan port server
SERVER_PORT = 9999
SERVER_PASSWORD = "123"
BUFFER_SIZE = 4096
KEY_RC4 = "my_secure_key"  # Kunci enkripsi yang sama di client dan server

# Fungsi RC4 untuk enkripsi dan dekripsi
def rc4_encrypt_decrypt(key, data):
    S = list(range(256))
    j = 0
    out = []

    # Key-scheduling algorithm (KSA)
    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    # Pseudo-random generation algorithm (PRGA)
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

    return ''.join(out)

# Fungsi untuk mengirim pesan ke semua klien yang terhubung kecuali pengirim
def broadcast(server_socket, message, source_address, clients):
    for address in clients:
        if address != source_address:
            server_socket.sendto(message, address)

def main():
    # Mendapatkan alamat IP server secara otomatis
    SERVER_IP = socket.gethostbyname(socket.gethostname())
    print(f"Server berjalan di {SERVER_IP}:{SERVER_PORT}")

    # Membuat socket UDP untuk server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))  # Mengikat socket ke IP dan port

    clients = {}     # Dictionary untuk menyimpan klien yang terhubung
    usernames = {}   # Dictionary untuk menyimpan username dari klien

    while True:
        # Menerima pesan dari klien mana pun
        message, client_address = server_socket.recvfrom(BUFFER_SIZE)
        decoded_message = rc4_encrypt_decrypt(KEY_RC4, message.decode())  # Dekripsi pesan

        # Memeriksa apakah pesan berisi username dan memprosesnya
        if decoded_message.startswith("USERNAME:"):
            username = decoded_message.split(":", 1)[1]
            if username in usernames.values():
                response = rc4_encrypt_decrypt(KEY_RC4, "Username sudah dipakai. Silakan pilih username lain.")
                server_socket.sendto(response.encode(), client_address)
            else:
                usernames[client_address] = username
                response = rc4_encrypt_decrypt(KEY_RC4, "Username diterima.")
                server_socket.sendto(response.encode(), client_address)
            continue

        # Memeriksa apakah pesan berisi password dan memverifikasinya
        elif decoded_message.startswith("PASSWORD:"):
            password = decoded_message.split(":", 1)[1]
            if password == SERVER_PASSWORD:
                clients[client_address] = True  # Menandai klien sebagai terhubung
                print(f"Klien {client_address} terhubung dengan username '{usernames[client_address]}'.")
                response = rc4_encrypt_decrypt(KEY_RC4, "Password diterima. Anda terhubung.")
                server_socket.sendto(response.encode(), client_address)
            else:
                response = rc4_encrypt_decrypt(KEY_RC4, "Password salah. Silakan coba lagi.")
                server_socket.sendto(response.encode(), client_address)
            continue

        # Jika klien terhubung, kirimkan pesan mereka ke klien lainnya
        if client_address in clients:
            print(f"Pesan dari {client_address}: {decoded_message}")
            encrypted_message = rc4_encrypt_decrypt(KEY_RC4, decoded_message)
            broadcast(server_socket, encrypted_message.encode(), client_address, clients)

if __name__ == "__main__":
    main()