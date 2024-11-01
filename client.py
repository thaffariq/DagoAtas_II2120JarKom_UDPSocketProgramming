import threading
import socket

BUFFER_SIZE = 4096

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
            print(message.decode())
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
        client_socket.sendto(f"USERNAME:{username}".encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        response_message = response.decode()
        print(response_message)
        
        if response_message == "Username diterima.":
            break

    # Mengirim password ke server dan menunggu konfirmasi koneksi
    while True:
        password = input("Masukkan password: ")
        client_socket.sendto(f"PASSWORD:{password}".encode(), server_address)
        
        response, _ = client_socket.recvfrom(BUFFER_SIZE)
        response_message = response.decode()
        print(response_message)

        if response_message == "Password diterima. Anda terhubung.":
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
        client_socket.sendto(complete_message.encode(), server_address)

if __name__ == "__main__":
    main()