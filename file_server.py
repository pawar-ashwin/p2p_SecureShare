import socket
import os

def start_server(host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print(f'Server listening on {host}:{port}')
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                handle_client(conn)

def handle_client(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        command = data.decode('utf-8').split(' ')
        if command[0] == 'UPLOAD':
            receive_file(conn, command[1])
        elif command[0] == 'DOWNLOAD':
            send_file(conn, command[1])

def receive_file(conn, filename):
    with open(filename, 'wb') as f:
        print(f'Receiving {filename}...')
        while True:
            data = conn.recv(1024)
            if not data:
                break
            f.write(data)
    print(f'{filename} received.')

def send_file(conn, filename):
    if os.path.exists(filename):
        conn.sendall(f'SENDING {filename}'.encode('utf-8'))
        with open(filename, 'rb') as f:
            conn.sendfile(f)
        print(f'{filename} sent.')
    else:
        conn.sendall(b'FILE NOT FOUND')

if __name__ == "__main__":
    start_server()
