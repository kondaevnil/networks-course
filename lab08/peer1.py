from peer import StopAndWaitPeer
import time
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Stop and Wait example')
    parser.add_argument('--port1', type=int, default=5005, help='peer1 port')
    parser.add_argument('--port2', type=int, default=5006, help='peer2 port')
    parser.add_argument('--loss', type=float, default=0.3, help='peer loss')
    args = parser.parse_args()
    
    peer1 = StopAndWaitPeer(host='localhost', port=args.port1, 
                           peer_host='localhost', peer_port=args.port2,
                           packet_loss=args.loss)
    
    try:
        peer1.start_receiver('received_by_peer1.txt')
        
        time.sleep(2)
        
        peer1.send_file('sent_by_peer1.txt')
        
        time.sleep(5)
    finally:
        peer1.stop()
