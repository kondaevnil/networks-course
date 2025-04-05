import socket
import time
import argparse
import statistics

def run_udp_client(server_host: str = '127.0.0.1', server_port: int = 5005) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(1.0)
        
        print(f"\nPING {server_host}:{server_port}")
        print(f"Exchanging packets with {server_host} on port {server_port}:")
        
        rtt_history = []
        lost_packets = 0
        
        for sequence in range(1, 11):
            try:
                send_time = time.time()
                message = f"Ping {sequence} {send_time}"
                
                sock.sendto(message.encode(), (server_host, server_port))
                
                try:
                    data, addr = sock.recvfrom(1024)
                    recv_time = time.time()
                    rtt = (recv_time - send_time) * 1000
                    rtt_history.append(rtt)
                    
                    print(f"\nResponse from {addr[0]}: bytes={len(data)} time={rtt:.2f}ms min={min(rtt_history):.2f}ms max={max(rtt_history):.2f}ms avg={statistics.mean(rtt_history):.2f}ms")
                    
                except socket.timeout:
                    lost_packets += 1
                    print(f"\nRequest timeout for sequence {sequence}")
                    if rtt_history:
                        print(f"\nmin={min(rtt_history):.2f}ms max={max(rtt_history):.2f}ms avg={statistics.mean(rtt_history):.2f}ms")
                
            except KeyboardInterrupt:
                print("\nClient forced stop")
                break
            except Exception as e:
                print(f"Error: {e}")
                lost_packets += 1
        
        print("\n--- Final ping statistics for {} ---".format(server_host))
        print("    Packets: sent = {}, received = {}, lost = {} ({:.0f}% loss)".format(
            10, 
            10 - lost_packets, 
            lost_packets, 
            (lost_packets / 10) * 100
        ))
        
        if rtt_history:
            print("Final RTT values:")
            print("    Minimum = {:.2f}ms".format(min(rtt_history)))
            print("    Maximum = {:.2f}ms".format(max(rtt_history)))
            print("    Average = {:.2f}ms".format(statistics.mean(rtt_history)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='UDP client displaying RTT statistics after each response')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Server host')
    parser.add_argument('--port', type=int, default=5005, help='Server port')
    args = parser.parse_args()
    
    run_udp_client(server_host=args.host, server_port=args.port)
