import socket

# Client configuration
SERVER_HOST = "192.168.1.72"  # Replace with your system's IP
SERVER_PORT = 5001              # Should match the server's port

# File to save
FILENAME = "received_file.txt"  # Name for saving the received file

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_HOST, SERVER_PORT))

# Open the file to write the received content in binary mode
with open(FILENAME, "wb") as file:
    while True:
        # Receive file in chunks
        data = client_socket.recv(1024)
        if not data:
            break
        file.write(data)
    print("[*] File received and saved.")

# Close socket
client_socket.close()