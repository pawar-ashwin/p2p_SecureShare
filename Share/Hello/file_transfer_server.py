import socket
import os

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 5001  # Port for file transfer

# Directory where files are stored (owner's share path)
SHARE_PATH = "D:/SharedFiles"  # Change this to the actual share path

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"File Transfer Server running on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection established with {addr}")
            with client_socket:
                file_name = client_socket.recv(1024).decode()
                file_path = os.path.join(SHARE_PATH, file_name)

                if os.path.exists(file_path):
                    client_socket.send(b"FOUND")
                    with open(file_path, "rb") as f:
                        while chunk := f.read(1024):
                            client_socket.send(chunk)
                    print(f"File '{file_name}' sent to {addr}")
                else:
                    client_socket.send(b"NOT_FOUND")
                    print(f"File '{file_name}' not found.")

if __name__ == "__main__":
    start_server()
