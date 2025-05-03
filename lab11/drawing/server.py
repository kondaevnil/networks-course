import socket
import threading


def start_server(host: str, port: int):
    clients = []
    draw_history = []

    def broadcast(data):
        for client in clients[:]:
            try:
                client.sendall(data)
            except:
                clients.remove(client)


    def handle_client(conn, addr):
        print(f"[+] Client connected: {addr}")
        clients.append(conn)

        try:
            for past in draw_history:
                conn.sendall(past)
        except:
            print(f"[!] Error sending history to {addr}")
            clients.remove(conn)
            conn.close()
            return

        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                draw_history.append(data)
                broadcast(data)  # <- теперь всем, включая отправителя
        finally:
            print(f"[-] Client disconnected: {addr}")
            if conn in clients:
                clients.remove(conn)
            conn.close()


    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[✓] Server running on {host}:{port}")
    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[!] Server shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    host = input("Enter server host (default 0.0.0.0): ") or "0.0.0.0"
    port = int(input("Enter port (default 5000): ") or "5000")
    start_server(host, port)
