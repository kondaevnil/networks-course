import sys
import socket


def client_request(host, port, filename):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        request = f"GET /{filename} HTTP/1.1\r\nHost: {host}\r\n\r\n"
        client.sendall(request.encode())
        response = client.recv(4096)
        print(response.decode(errors='ignore'))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python client.py <host> <port> <filename>")
        sys.exit(1)

    client_request(sys.argv[1], int(sys.argv[2]), sys.argv[3])
