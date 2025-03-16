import smtplib
import sys
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(recipient: str, subject: str, message: str, format: str = "txt"):
    # Для работы нужно добавить в файл .env следующие переменные:
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print("Error: Email credentials are missing!")
        return
    
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = recipient
    msg['Subject'] = subject
    
    if format == "html":
        msg.attach(MIMEText(message, 'html'))
    else:
        msg.attach(MIMEText(message, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_client.py <recipient>")
        sys.exit()

    recipient = sys.argv[1]
    subject = "Test Email"
    message_txt = "Hello! This is a test email in plain text."
    message_html = """
    <html>
        <body>
            <h1>Hello!</h1>
            <p>This is a test email in <b>HTML format</b>.</p>
        </body>
    </html>
    """
    send_email(recipient, subject, message_txt, "txt")
    send_email(recipient, subject, message_html, "html")
