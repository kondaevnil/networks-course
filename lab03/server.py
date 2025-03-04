import os
import socket
import sys
import threading
from concurrent.futures import ThreadPoolExecutor


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_client(conn):
    try:
        request = conn.recv(1024).decode()
        lines = request.split("\r\n")
        if len(lines) > 0:
            parts = lines[0].split()
            if len(parts) >= 2 and parts[0] == "GET":
                filename = parts[1].lstrip("/")
                filepath = os.path.join(BASE_DIR, filename)
                print(filepath)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    with open(filepath, "rb") as f:
                        content = f.read()
                    response = ("HTTP/1.1 200 OK\r\n"
                                "Content-Type: text/plain\r\n"
                                "Content-Length: " + str(len(content)) + "\r\n"
                                "\r\n").encode() + content
                else:
                    response = ("HTTP/1.1 404 Not Found\r\n"
                                "Content-Type: text/plain\r\n"
                                "Content-Length: 13\r\n"
                                "\r\n"
                                "404 Not Found").encode()
                conn.sendall(response)
    finally:
        conn.close()


def serve(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", port))
        s.listen(1)
        print(f"Server listening on port {port}...")
        while True:
            conn, _ = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()

def serve_limited(port, concurrency_level):
    executor = ThreadPoolExecutor(max_workers=concurrency_level)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind(("0.0.0.0", port))
        server.listen(5)
        print(f"Server listening on port {port} with concurrency {concurrency_level}...")
        while True:
            conn, _ = server.accept()
            executor.submit(handle_client, conn)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python server.py <port>")
        sys.exit(1)
    elif len(sys.argv) == 2:
        port = int(sys.argv[1])
        serve(port)
    else:
        port = int(sys.argv[1])
        conc_lvl = int(sys.argv[2])
        serve_limited(port, conc_lvl)

