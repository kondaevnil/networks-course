import os
import ssl
import socket
import base64
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_email(to_email, subject, message, image_path):
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
    
    # Отправка письма
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
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = to_email
    msg['Subject'] = subject
    
    text_part = MIMEText(message, 'plain')
    msg.attach(text_part)
    
    with open(image_path, 'rb') as img_file:
        img_data = img_file.read()
    image_part = MIMEImage(img_data, name=os.path.basename(image_path))
    msg.attach(image_part)
    
    email_message = msg.as_string()
    client_socket.sendall(email_message.encode())
    client_socket.sendall(b"\r\n.\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.sendall(b"QUIT\r\n")
    recv = client_socket.recv(1024).decode()
    print(recv)
    
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python post_client.py <recipient> <image_path>")
        sys.exit()

    recipient = sys.argv[1]
    img_path = sys.argv[2]
    subject = "Test Email"
    message_txt = "Hello! This is a test email in plain text."
    send_email(recipient, subject, message_txt, img_path)
