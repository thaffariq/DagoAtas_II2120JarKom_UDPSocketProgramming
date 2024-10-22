import threading
import socket

# Fungsi untuk menerima pesan dari server
def recv_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            decoded_message = message.decode()

            if decoded_message == "PASSWORD_ACCEPTED":
                print("Password accepted. You are now in the chat room.")
            elif decoded_message == "PASSWORD_REJECTED":
                print("Wrong password! Try again.")
            else:
                print(decoded_message)  # Tampilkan pesan dari klien lain
        except:
            print("Connection lost.")
            break

# Fungsi untuk mengirimkan password ke server
def send_password(client_socket, server_address):
    # Hardcoded password
    server_password = "1234"
    client_socket.sendto(f"PASSWORD:{server_password}".encode(), server_address)

    response, _ = client_socket.recvfrom(1024)
    decoded_response = response.decode()

    if decoded_response == "PASSWORD_ACCEPTED":
        return True
    else:
        return False

# Fungsi utama untuk klien
def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("localhost", 2305)

    username = input("Enter username: ")

    # Kirim dan validasi password
    password_valid = send_password(client_socket, server_address)

    if not password_valid:
        print("Failed to authenticate. Exiting...")
        return

    # Mulai thread untuk menerima pesan dari server
    threading.Thread(target=recv_messages, args=(client_socket,), daemon=True).start()

    # Loop untuk mengirim pesan
    while True:
        message = input()
        if message.lower() == "exit":
            print("You left the chat room.")
            break

        # Format pesan yang dikirim
        formatted_message = f"{username}: {message}"
        client_socket.sendto(formatted_message.encode(), server_address)

if __name__ == "__main__":
    main()
