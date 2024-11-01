import threading
import socket

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

def is_valid_ip(ip):
    parts = ip.split(".")
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

def is_valid_port(port):
    return port.isdigit() and 1024 <= int(port) <= 65535

def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(BUFFER_SIZE)
            decrypted_message = rc4_encrypt_decrypt(KEY_RC4, message.decode())
            print(decrypted_message)  # Menampilkan pesan tanpa checksum
        except:
            print("Terputus dari server.")
            break

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    while True:
        server_ip = input("Masukkan IP server: ")
        server_port = input("Masukkan port server: ")
        
        if is_valid_ip(server_ip) and is_valid_port(server_port):
            server_address = (server_ip, int(server_port))
            break
        else:
            print("IP atau port tidak valid. Silakan coba lagi.")

    while True:
        username = input("Masukkan username: ")
        encrypted_username = rc4_encrypt_decrypt(KEY_RC4, f"USERNAME:{username}")
        client_socket.sendto(encrypted_username.encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        decrypted_response = rc4_encrypt_decrypt(KEY_RC4, response.decode())
        print(decrypted_response)
        
        if decrypted_response == "Username diterima.":
            break

    while True:
        password = input("Masukkan password: ")
        encrypted_password = rc4_encrypt_decrypt(KEY_RC4, f"PASSWORD:{password}")
        client_socket.sendto(encrypted_password.encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        decrypted_response = rc4_encrypt_decrypt(KEY_RC4, response.decode())
        print(decrypted_response)

        if decrypted_response == "Password diterima. Anda terhubung.":
            break

    threading.Thread(target=recv_messages, args=(client_socket,)).start()

    while True:
        message = input()
        if message.lower() == "exit":
            print("Anda telah meninggalkan ruang obrolan.")
            break

        checksum = calculate_checksum(message)
        complete_message = f"{message}:{checksum}"
        encrypted_message = rc4_encrypt_decrypt(KEY_RC4, complete_message)
        client_socket.sendto(encrypted_message.encode(), server_address)

if __name__ == "__main__":
    main()