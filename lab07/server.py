import socket
import random
import argparse

def run_udp_server(host: str = '127.0.0.1', port: int = 5005) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"UDP server started on {host}:{port}")
        
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(f"Received message from {addr}: {data.decode()}")
                
                if random.random() < 0.2:
                    print(f"Packet from {addr} lost")
                    continue
                
                response = data.decode().upper().encode()
                sock.sendto(response, addr)
                print(f"Sent response to {addr}: {response.decode()}")
                
            except KeyboardInterrupt:
                print("Server stopped")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UDP server for echo requests')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to listen on')
    parser.add_argument('--port', type=int, default=5005, help='Port to listen on')
    args = parser.parse_args()
    
    run_udp_server(host=args.host, port=args.port)
