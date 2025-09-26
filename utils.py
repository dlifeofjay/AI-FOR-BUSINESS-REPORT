import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

load_dotenv()

def load_config():
    config = {
        "server" : os.getenv("SQL_SERVER"),
        "database" : os.getenv("SQL_DATABASE"),
        "to_email" : os.getenv("TO_EMAIL"),
        "from_email" : os.getenv("FROM_EMAIL"),
        "smtp_server" : os.getenv("SMTP_SERVER"),
        "smtp_port" : int(os.getenv("SMTP_PORT", "587")),
        "smtp_user" : os.getenv("SMTP_USER"),
        "smtp_pass" : os.getenv("SMTP_PASS"),
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
    }
    return config

def send_email(subject, body, attachment_path=None):
    cfg = load_config()
    msg = MIMEMultipart()
    msg['From'] = cfg['from_email']
    msg['To'] = cfg['to_email']
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if attachment_path:
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
        msg.attach(part)

    with smtplib.SMTP(cfg["smtp_server"], cfg["smtp_port"]) as server:
        server.starttls()
        server.login(cfg["smtp_user"], cfg["smtp_pass"])
        server.send_message(msg)