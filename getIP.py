import socket

def get_local_ip():
    try:
        # Create a socket to determine the local machine IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        
        # Try to connect to an arbitrary external address (we don't need to actually connect)
        s.connect(('8.8.8.8', 80))  # Google's public DNS server
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error: {e}")
        return None

# Get and print the local IP address
local_ip = get_local_ip()
if local_ip:
    print(f"Local IP Address: {local_ip}")
else:
    print("Could not determine local IP address.")
