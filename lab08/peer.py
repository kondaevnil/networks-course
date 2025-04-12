import socket
import random
import logging
import time
import threading
import os

class StopAndWaitPeer:
    def __init__(self, host='localhost', port=5000, peer_host='localhost', peer_port=5001, 
                 timeout=2, packet_loss=0.3, packet_size=1024):
        self.host = host
        self.port = port
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.timeout = timeout
        self.packet_loss = packet_loss
        self.packet_size = packet_size
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(self.timeout)
        self.seq_num = 0
        self.expected_seq_num = 0
        self.max_retries = 100
        self.logger = self._setup_logger('peer')
        self.receive_thread = None
        self.running = False
        
    def _setup_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    
    def _simulate_packet_loss(self):
        return random.random() < self.packet_loss
    
    def _send_packet(self, data, seq_num=None):
        if seq_num is None:
            seq_num = self.seq_num
        
        packet = seq_num.to_bytes(2, byteorder='big') + data
        
        if self._simulate_packet_loss():
            self.logger.warning(f"Packet {seq_num} lost (simulated)")
            return False
        
        self.sock.sendto(packet, (self.peer_host, self.peer_port))
        self.logger.info(f"Sent packet {seq_num} to {self.peer_host}:{self.peer_port}")
        return True
    
    def _send_ack(self, seq_num):
        ack = f"ACK:{seq_num}".encode()
        
        if self._simulate_packet_loss():
            self.logger.warning(f"ACK {seq_num} lost (simulated)")
            return
        
        self.sock.sendto(ack, (self.peer_host, self.peer_port))
        self.logger.info(f"Sent ACK {seq_num} to {self.peer_host}:{self.peer_port}")
    
    def _wait_for_ack(self, expected_seq_num):
        try:
            ack_data, _ = self.sock.recvfrom(1024)
            ack_str = ack_data.decode()
            
            if ack_str.startswith("ACK:"):
                ack_seq_num = int(ack_str.split(":")[1])
                self.logger.info(f"Received ACK {ack_seq_num}")
                return ack_seq_num == expected_seq_num
            else:
                self.logger.warning(f"Invalid ACK format: {ack_str}")
                return False
        except socket.timeout:
            self.logger.warning("Timeout waiting for ACK")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for ACK: {e}")
            return False
    
    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                self.logger.info(f"Starting file transfer to {self.peer_host}:{self.peer_port}")
                
                while True:
                    data = f.read(self.packet_size - 2)
                    if not data:
                        break
                    
                    retries = 0
                    while retries < self.max_retries:
                        if not self._send_packet(data):
                            retries += 1
                            continue
                        
                        if self._wait_for_ack(self.seq_num):
                            self.seq_num = 1 - self.seq_num
                            break
                        
                        retries += 1
                        self.logger.warning(f"Retrying packet {self.seq_num}, attempt {retries}")
                        time.sleep(0.1)
                    
                    if retries >= self.max_retries:
                        raise Exception(f"Max retries ({self.max_retries}) exceeded for packet {self.seq_num}")
                
                self._send_end_of_transmission()
            
            self.logger.info("File transfer completed successfully")
        except Exception as e:
            self.logger.error(f"Error sending file: {e}")
    
    def _send_end_of_transmission(self):
        retries = 0
        while retries < self.max_retries / 10:
            self.sock.sendto(b"END_OF_TRANSMISSION", (self.peer_host, self.peer_port))
            self.logger.info("Sent end of transmission signal")
            
            if self._wait_for_ack(self.seq_num):
                self.logger.info("Received final ACK")
                return
            retries += 1
            continue
        
        self.logger.error("Failed to receive final ACK")
    
    def _receive_file(self, output_file):
        with open(output_file, 'wb') as f:
            self.logger.info(f"Ready to receive file from {self.peer_host}:{self.peer_port}")
            
            while self.running:
                try:
                    data, addr = self.sock.recvfrom(self.packet_size)
                    
                    if data == b"END_OF_TRANSMISSION":
                        self.logger.info("Received end of transmission signal")
                        self._send_ack(self.expected_seq_num)
                        break
                    
                    seq_num = int.from_bytes(data[:2], byteorder='big')
                    packet_data = data[2:]
                    
                    self.logger.info(f"Received packet {seq_num} from {addr}")
                    
                    if seq_num == self.expected_seq_num:
                        f.write(packet_data)
                        self._send_ack(seq_num)
                        self.expected_seq_num = 1 - self.expected_seq_num
                        self.logger.info(f"Accepted packet {seq_num}, expecting {self.expected_seq_num} next")
                    else:
                        self._send_ack(1 - self.expected_seq_num)
                        self.logger.warning(f"Received out-of-order packet {seq_num}, expected {self.expected_seq_num}")
                
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"Error receiving file: {e}")
                    break
        
        self.logger.info(f"File saved as {output_file}")
    
    def start_receiver(self, output_file):
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_file, args=(output_file,))
        self.receive_thread.start()
        self.logger.info("Receiver thread started")
    
    def stop(self):
        self.running = False
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join()
        self.sock.close()
        self.logger.info("Peer stopped")
