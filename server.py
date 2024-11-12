import socket

# Server configuration
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5001        # Arbitrary port number, make sure it's open

# File to send
FILENAME = "name.txt"  # Change this to the file you want to send

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Listen for incoming connections (can handle 1 client at a time)
server_socket.listen(1)
print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

# Accept client connection
client_socket, client_address = server_socket.accept()
print(f"[+] {client_address} is connected.")

# Open the file to be sent in binary mode
with open(FILENAME, "rb") as file:
    # Send the file in chunks
    while chunk := file.read(1024):  # Read 1024 bytes at a time
        client_socket.send(chunk)
    print("[*] File transfer completed.")

# Close sockets
client_socket.close()
server_socket.close()