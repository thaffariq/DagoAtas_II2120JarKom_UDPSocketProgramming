import socket
import threading
import csv
import time

SERVER_IP = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 9999
SERVER_PASSWORD = "123"
BUFFER_SIZE = 4096
KEY_RC4 = "my_secure_key"
HISTORY_FILE = "chat_history.csv"

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

class Server:
    def __init__(self, ip, port, password):
        self.ip = ip
        self.port = port
        self.password = password
        self.clients = {}
        self.usernames = {}
        self.cipher = RC4Cipher(KEY_RC4)

    def calculate_checksum(self, data):
        return sum(ord(char) for char in data) % 256

    def broadcast(self, message, source_address):
        for address in self.clients:
            if address != source_address:
                self.server_socket.sendto(message, address)

    def save_message(self, username, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(HISTORY_FILE, "a", newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, username, message])

    def send_history_to_client(self, client_address):
        try:
            with open(HISTORY_FILE, "r") as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) == 3:
                        timestamp, username, message = row
                        message_to_send = f"[{timestamp}] {username}: {message}"
                        encrypted_message = self.cipher.encrypt_decrypt(message_to_send)
                        self.server_socket.sendto(encrypted_message.encode(), client_address)
        except FileNotFoundError:
            pass

    def handle_message(self, message, client_address):
        decrypted_message = self.cipher.encrypt_decrypt(message.decode())

        if decrypted_message.startswith("USERNAME:"):
            username = decrypted_message.split(":", 1)[1]
            if username in self.usernames.values():
                response = self.cipher.encrypt_decrypt("Username sudah dipakai. Silakan pilih username lain.")
                self.server_socket.sendto(response.encode(), client_address)
            else:
                self.usernames[client_address] = username
                response = self.cipher.encrypt_decrypt("Username diterima.")
                self.server_socket.sendto(response.encode(), client_address)
                self.send_history_to_client(client_address)
            return

        elif decrypted_message.startswith("PASSWORD:"):
            password = decrypted_message.split(":", 1)[1]
            if password == self.password:
                self.clients[client_address] = True
                print(f"Klien {client_address} terhubung dengan username '{self.usernames[client_address]}'.")
                response = self.cipher.encrypt_decrypt("Password diterima. Anda terhubung.")
                self.server_socket.sendto(response.encode(), client_address)
            else:
                response = self.cipher.encrypt_decrypt("Password salah. Silakan coba lagi.")
                self.server_socket.sendto(response.encode(), client_address)
            return

        if client_address in self.clients:
            try:
                data, received_checksum = decrypted_message.rsplit(":", 1)
                calculated_checksum = self.calculate_checksum(data)

                if calculated_checksum == int(received_checksum):
                    username = self.usernames[client_address]
                    print(f"Pesan dari {client_address} {username}: '{data}' dengan checksum valid: {received_checksum}")

                    self.save_message(username, data)

                    message_to_send = f"{username}: {data}"
                    encrypted_message = self.cipher.encrypt_decrypt(message_to_send)
                    self.broadcast(encrypted_message.encode(), client_address)
                else:
                    print("Pesan rusak: checksum tidak sesuai.")
                    response = self.cipher.encrypt_decrypt("Pesan rusak: checksum tidak sesuai.")
                    self.server_socket.sendto(response.encode(), client_address)
            except ValueError:
                print("Format pesan tidak valid.")
                response = self.cipher.encrypt_decrypt("Format pesan tidak valid.")
                self.server_socket.sendto(response.encode(), client_address)

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.ip, self.port))
        print(f"Server berjalan di {self.ip}:{self.port}")

        while True:
            message, client_address = self.server_socket.recvfrom(BUFFER_SIZE)
            self.handle_message(message, client_address)

if __name__ == "__main__":
    server = Server(SERVER_IP, SERVER_PORT, SERVER_PASSWORD)
    server.run()