import socket
import threading

BUFFER_SIZE = 4096
KEY_RC4 = "my_secure_key"

class RC4Cipher:
    def __init__(self, key):
        self.key = key

    def encrypt_decrypt(self, data):
        S = list(range(256))
        j = 0
        out = []

        for i in range(256):
            j = (j + S[i] + ord(self.key[i % len(self.key)])) % 256
            S[i], S[j] = S[j], S[i]

        i = j = 0
        for char in data:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

        return ''.join(out)

class Client:
    def __init__(self, buffer_size, key):
        self.buffer_size = buffer_size
        self.cipher = RC4Cipher(key)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def calculate_checksum(self, data):
        return sum(ord(char) for char in data) % 256

    def is_valid_ip(self, ip):
        parts = ip.split(".")
        return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

    def is_valid_port(self, port):
        return port.isdigit() and 1024 <= int(port) <= 65535

    def recv_messages(self):
        while True:
            try:
                message, _ = self.client_socket.recvfrom(self.buffer_size)
                decrypted_message = self.cipher.encrypt_decrypt(message.decode())
                print(decrypted_message)
            except:
                print("Terputus dari server.")
                break

    def connect_to_server(self):
        while True:
            server_ip = input("Masukkan IP server: ")
            server_port = input("Masukkan port server: ")

            if self.is_valid_ip(server_ip) and self.is_valid_port(server_port):
                self.server_address = (server_ip, int(server_port))
                break
            else:
                print("IP atau port tidak valid. Silakan coba lagi.")

        while True:
            username = input("Masukkan username: ")
            encrypted_username = self.cipher.encrypt_decrypt(f"USERNAME:{username}")
            self.client_socket.sendto(encrypted_username.encode(), self.server_address)

            response, _ = self.client_socket.recvfrom(self.buffer_size)
            decrypted_response = self.cipher.encrypt_decrypt(response.decode())
            print(decrypted_response)

            if decrypted_response == "Username diterima.":
                break

        while True:
            password = input("Masukkan password: ")
            encrypted_password = self.cipher.encrypt_decrypt(f"PASSWORD:{password}")
            self.client_socket.sendto(encrypted_password.encode(), self.server_address)

            response, _ = self.client_socket.recvfrom(self.buffer_size)
            decrypted_response = self.cipher.encrypt_decrypt(response.decode())
            print(decrypted_response)

            if decrypted_response == "Password diterima. Anda terhubung.":
                break

        threading.Thread(target=self.recv_messages).start()

        while True:
            message = input()
            if message.lower() == "exit":
                print("Anda telah meninggalkan ruang obrolan.")
                break

            checksum = self.calculate_checksum(message)
            complete_message = f"{message}:{checksum}"
            encrypted_message = self.cipher.encrypt_decrypt(complete_message)
            self.client_socket.sendto(encrypted_message.encode(), self.server_address)

if __name__ == "__main__":
    client = Client(BUFFER_SIZE, KEY_RC4)
    client.connect_to_server()