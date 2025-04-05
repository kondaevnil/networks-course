import socket
import time
import argparse
from datetime import datetime

def run_udp_client(server_host: str = '127.0.0.1', server_port: int = 5005) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1.0)
        
        print(f"PING {server_host}:{server_port}")
        
        for sequence in range(1, 11):
            try:
                send_time = time.time()
                gt = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(send_time))
                message = f"Ping {sequence} {gt}"
                
                sock.sendto(message.encode(), (server_host, server_port))
                
                try:
                    data, addr = sock.recvfrom(1024)
                    recv_time = time.time()
                    rtt = (recv_time - send_time) * 1000
                    
                    print(f"Reply from {addr[0]}: {data.decode()}")
                    print(f"Round trip time (RTT): {rtt:.2f} ms")
                    
                except socket.timeout:
                    print(f"Request {sequence} timed out")
                
            except KeyboardInterrupt:
                print("\nClient stopped")
                break
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UDP client for echo requests')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host')
    parser.add_argument('--port', type=int, default=5005, help='Server port')
    args = parser.parse_args()
    
    run_udp_client(server_host=args.host, server_port=args.port)
