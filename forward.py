import miniupnpc

def forward_port(internal_ip, external_port, internal_port):
    # Initialize the UPnP client
    upnp = miniupnpc.UPnP()
    
    # Discover UPnP devices
    upnp.discover()
    
    # Select the first found device
    upnp.selectigd()

    # Add port mapping: forward external port to internal port
    upnp.addportmapping(external_port, 'TCP', internal_ip, internal_port, 'Python Port Forwarding', '')
    print(f"Port {external_port} forwarded to {internal_ip}:{internal_port}")

# Example usage
internal_ip = '192.168.1.72'  # Your server's local IP address
external_port = 5001         # The port you want to forward externally
internal_port = 5001         # The port on the internal server

forward_port(internal_ip, external_port, internal_port)