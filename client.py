import threading
import socket

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

# Memeriksa format IP yang valid
def is_valid_ip(ip):
    parts = ip.split(".")
    if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
        return True
    return False

# Memeriksa rentang nomor port yang valid
def is_valid_port(port):
    return port.isdigit() and 1024 <= int(port) <= 65535

# Thread untuk menerima pesan secara terus-menerus
def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            decrypted_message = rc4_encrypt_decrypt(KEY_RC4, message.decode())  # Dekripsi pesan
            print(decrypted_message)
        except:
            print("Terputus dari server.")
            break

def main():
    # Membuat socket UDP untuk klien
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        server_ip = input("Masukkan IP server: ")
        server_port = input("Masukkan port server: ")
        
        if is_valid_ip(server_ip) and is_valid_port(server_port):
            server_address = (server_ip, int(server_port))
            break
        else:
            print("IP atau port tidak valid. Silakan coba lagi.")

    # Mengirim username ke server dan menunggu konfirmasi
    while True:
        username = input("Masukkan username: ")
        encrypted_username = rc4_encrypt_decrypt(KEY_RC4, f"USERNAME:{username}")
        client_socket.sendto(encrypted_username.encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        decrypted_response = rc4_encrypt_decrypt(KEY_RC4, response.decode())
        print(decrypted_response)
        
        if decrypted_response == "Username diterima.":
            break

    # Mengirim password ke server dan menunggu konfirmasi koneksi
    while True:
        password = input("Masukkan password: ")
        encrypted_password = rc4_encrypt_decrypt(KEY_RC4, f"PASSWORD:{password}")
        client_socket.sendto(encrypted_password.encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        decrypted_response = rc4_encrypt_decrypt(KEY_RC4, response.decode())
        print(decrypted_response)

        if decrypted_response == "Password diterima. Anda terhubung.":
            break

    # Memulai thread untuk mendengarkan pesan yang masuk
    threading.Thread(target=recv_messages, args=(client_socket,)).start()

    # Mengirim pesan secara terus-menerus hingga pengguna mengetik "exit"
    while True:
        message = input()
        if message.lower() == "exit":
            print("Anda telah meninggalkan ruang obrolan.")
            break

        complete_message = f"{username}: {message}"
        encrypted_message = rc4_encrypt_decrypt(KEY_RC4, complete_message)
        client_socket.sendto(encrypted_message.encode(), server_address)

if __name__ == "__main__":
    main()