import socket
import os

# Server configuration
SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
SERVER_PORT = 5001       # Port number for communication

# Function to handle client connection and file transfer
def handle_client(client_socket):
    # Receive the filename requested by the client
    requested_file = client_socket.recv(1024).decode()
    print(f"[*] Client requested the file: {requested_file}")

    # Check if the file exists
    file_path = os.path.join('C:\\Restaurant Project Resources\\', requested_file)
    if os.path.isfile(file_path):
        # Open the requested file in binary mode
        with open(file_path, "rb") as file:
            # Send the file in chunks to the client
            while chunk := file.read(1024):
                client_socket.send(chunk)
        print(f"[*] File '{requested_file}' sent successfully.")
    else:
        # If file doesn't exist, send an error message to the client
        error_message = f"Error: The file '{requested_file}' does not exist."
        client_socket.send(error_message.encode())
        print(f"[!] File '{requested_file}' not found. Sent error message.")

    # Close the client connection after sending the file
    client_socket.close()
    print(f"[*] Client connection closed after file transfer.")

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_HOST, SERVER_PORT))

# Listen for incoming connections (can handle 1 client at a time)
server_socket.listen(1)
print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

# Main server loop to handle one client at a time
while True:
    # Accept client connection
    client_socket, client_address = server_socket.accept()
    print(f"[+] {client_address} is connected.")

    # Handle the client (send file, close connection)
    handle_client(client_socket)

    # After handling the client, the server will return to listening for new connections
    print("[*] Ready for new connections...\n")

# Close the server socket after breaking the loop (this won't be reached unless the server stops)
server_socket.close()
