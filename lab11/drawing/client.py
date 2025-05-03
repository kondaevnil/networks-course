import socket
import threading
import tkinter as tk


def run_client(server_ip: str, port: int):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, port))
        print(f"[✓] Connected to {server_ip}:{port}")
    except Exception as e:
        print(f"[✗] Connection failed: {e}")
        return

    root = tk.Tk()
    root.title(f"Client - {server_ip}:{port}")
    global canvas
    canvas = tk.Canvas(root, width=800, height=600, bg='white')
    canvas.pack()

    prev = {'x': None, 'y': None}

    def send_draw(event):
        if prev['x'] is not None and prev['y'] is not None:
            message = f"{prev['x']},{prev['y']},{event.x},{event.y}"
            try:
                sock.sendall(message.encode())
            except:
                pass
        prev['x'], prev['y'] = event.x, event.y

    def reset_prev(event):
        prev['x'] = None
        prev['y'] = None

    def draw_line(x1, y1, x2, y2):
        canvas.create_line(x1, y1, x2, y2, fill='black', width=4, capstyle=tk.ROUND, smooth=True)

    def receive_drawings():
        while True:
            try:
                data = sock.recv(1024)
                if not data:
                    break
                coords = data.decode().strip().split(',')
                if len(coords) == 4:
                    x1, y1, x2, y2 = map(int, coords)
                    draw_line(x1, y1, x2, y2)
            except:
                break

    canvas.bind("<B1-Motion>", send_draw)
    canvas.bind("<ButtonRelease-1>", reset_prev)

    threading.Thread(target=receive_drawings, daemon=True).start()
    root.mainloop()


if __name__ == "__main__":
    server_ip = input("Enter server IP (default 127.0.0.1): ") or "127.0.0.1"
    port = int(input("Enter server port (default 5000): ") or "5000")
    run_client(server_ip, port)
