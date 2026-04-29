import re
import smtplib
import socket
from email.message import EmailMessage

from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

from .email_templates import build_confirmation_email

EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
CONFIRM_EMAIL_SALT = "confirm-email"


def is_valid_email(email):
    if not email or not EMAIL_PATTERN.match(email):
        return False

    domain = email.rsplit("@", 1)[1]

    try:
        import dns.resolver

        dns.resolver.resolve(domain, "MX")
        return True
    except ImportError:
        pass
    except Exception:
        return False

    try:
        socket.getaddrinfo(domain, None)
        return True
    except socket.gaierror:
        return False


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt=CONFIRM_EMAIL_SALT)


def get_email_from_confirmation_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, salt=CONFIRM_EMAIL_SALT, max_age=max_age)


def send_confirmation_email(user):
    token = generate_confirmation_token(user.email)
    confirmation_url = url_for("main.confirm_email", token=token, _external=True)
    subject = "Confirm your RecipeHub email"
    body, html_body = build_confirmation_email(user.username, confirmation_url)

    mail_server = current_app.config.get("MAIL_SERVER")
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    if not mail_server:
        print(f"Email confirmation link for {user.email}: {confirmation_url}")
        return confirmation_url

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = user.email
    message.set_content(body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(mail_server, current_app.config["MAIL_PORT"]) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        if mail_username and mail_password:
            smtp.login(mail_username, mail_password)
        smtp.send_message(message)

    return confirmation_url
