import socket


def send_command(command, host='127.0.0.1', port=65432):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        client_socket.sendall(command.encode('utf-8'))
        data = client_socket.recv(1024)
        print(f"result:\n{data.decode('utf-8')}")


if __name__ == "__main__":
    command = input("input cmd: ")
    send_command(command)