import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)


def send_invite_email(to_email: str, password: str):
    # Wenn SMTP nicht konfiguriert ist, einfach nur in der Konsole ausgeben
    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM]):
        print("SMTP nicht konfiguriert. Würde Einladung schicken an:", to_email)
        print("Passwort:", password)
        return

    msg = EmailMessage()
    msg["Subject"] = "Zugangsdaten zum Kleingarten-Portal"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    msg.set_content(
        f"""Hallo,

hier sind deine Zugangsdaten für das Kleingarten-Mitgliederportal:

E-Mail: {to_email}
Passwort: {password}

Bitte nach dem ersten Login das Passwort ändern.

Viele Grüße
Dein Kleingartenverein
"""
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
