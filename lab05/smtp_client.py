import os
import ssl
import socket
import base64
import sys

def send_email(to_email, subject, message):
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT]):
        raise ValueError("One or more environment variables are missing")
    
    client_socket = socket.create_connection((SMTP_SERVER, SMTP_PORT))
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(b"EHLO client\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(b"STARTTLS\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    context = ssl.create_default_context()
    client_socket = context.wrap_socket(client_socket, server_hostname=SMTP_SERVER)
    
    client_socket.sendall(b"EHLO client\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    auth_command = "AUTH LOGIN\r\n".encode()
    client_socket.sendall(auth_command)
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(base64.b64encode(EMAIL_SENDER.encode()) + b"\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(base64.b64encode(EMAIL_PASSWORD.encode()) + b"\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    mail_from = f"MAIL FROM:<{EMAIL_SENDER}>\r\n".encode()
    client_socket.sendall(mail_from)
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    rcpt_to = f"RCPT TO:<{to_email}>\r\n".encode()
    client_socket.sendall(rcpt_to)
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(b"DATA\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    email_message = f"Subject: {subject}\r\n\r\n{message}\r\n.\r\n"
    client_socket.sendall(email_message.encode())
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(b"QUIT\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_client.py <recipient>")
        sys.exit()

    recipient = sys.argv[1]
    subject = "Test Email"
    message_txt = "Hello! This is a test email in plain text."
    send_email(recipient, subject, message_txt)
