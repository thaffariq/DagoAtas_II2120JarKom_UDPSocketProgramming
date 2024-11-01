import socket
import threading

# Mendapatkan alamat IP server secara otomatis
SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999
SERVER_PASSWORD = "123"
BUFFER_SIZE = 4096
KEY_RC4 = "my_secure_key"

def rc4_encrypt_decrypt(key, data):
    S = list(range(256))
    j = 0
    out = []

    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

    return ''.join(out)

def calculate_checksum(data):
    return sum(ord(char) for char in data) % 256

def broadcast(server_socket, message, source_address, clients):
    for address in clients:
        if address != source_address:
            server_socket.sendto(message, address)

def main():
    # Membuat socket UDP untuk server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    print(f"Server berjalan di {SERVER_IP}:{SERVER_PORT}")

    clients = {}
    usernames = {}

    while True:
        message, client_address = server_socket.recvfrom(BUFFER_SIZE)
        decrypted_message = rc4_encrypt_decrypt(KEY_RC4, message.decode())
        
        if decrypted_message.startswith("USERNAME:"):
            username = decrypted_message.split(":", 1)[1]
            if username in usernames.values():
                response = rc4_encrypt_decrypt(KEY_RC4, "Username sudah dipakai. Silakan pilih username lain.")
                server_socket.sendto(response.encode(), client_address)
            else:
                usernames[client_address] = username
                response = rc4_encrypt_decrypt(KEY_RC4, "Username diterima.")
                server_socket.sendto(response.encode(), client_address)
            continue

        elif decrypted_message.startswith("PASSWORD:"):
            password = decrypted_message.split(":", 1)[1]
            if password == SERVER_PASSWORD:
                clients[client_address] = True
                print(f"Klien {client_address} terhubung dengan username '{usernames[client_address]}'.")
                response = rc4_encrypt_decrypt(KEY_RC4, "Password diterima. Anda terhubung.")
                server_socket.sendto(response.encode(), client_address)
            else:
                response = rc4_encrypt_decrypt(KEY_RC4, "Password salah. Silakan coba lagi.")
                server_socket.sendto(response.encode(), client_address)
            continue

        if client_address in clients:
            try:
                # Memisahkan data dan checksum yang diterima
                data, received_checksum = decrypted_message.rsplit(":", 1)
                calculated_checksum = calculate_checksum(data)
                
                # Menampilkan pesan, username, dan checksum di server
                if calculated_checksum == int(received_checksum):
                    username = usernames[client_address]
                    print(f"Pesan dari {client_address} {username}: '{data}' dengan checksum valid: {received_checksum}")
                    
                    # Mempersiapkan pesan untuk dikirim ke klien lain tanpa checksum
                    message_to_send = f"{username}: {data}"
                    encrypted_message = rc4_encrypt_decrypt(KEY_RC4, message_to_send)
                    broadcast(server_socket, encrypted_message.encode(), client_address, clients)
                else:
                    print("Pesan rusak: checksum tidak sesuai.")
                    response = rc4_encrypt_decrypt(KEY_RC4, "Pesan rusak: checksum tidak sesuai.")
                    server_socket.sendto(response.encode(), client_address)
            except ValueError:
                print("Format pesan tidak valid.")
                response = rc4_encrypt_decrypt(KEY_RC4, "Format pesan tidak valid.")
                server_socket.sendto(response.encode(), client_address)

if __name__ == "__main__":
    main()