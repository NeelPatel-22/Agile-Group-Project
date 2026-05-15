import re
import smtplib
from email.message import EmailMessage

from flask import current_app, url_for
from itsdangerous import URLSafeTimedSerializer

from .email_templates import build_confirmation_email, build_email_change_email, build_password_reset_email

EMAIL_PATTERN = re.compile(r"^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$", re.IGNORECASE)
CONFIRM_EMAIL_SALT = "confirm-email"
EMAIL_CHANGE_SALT = "change-email"
PASSWORD_RESET_SALT = "reset-password"


def is_valid_email(email):
    return bool(email and EMAIL_PATTERN.match(email))


def generate_confirmation_token(payload):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(payload, salt=CONFIRM_EMAIL_SALT)


def get_payload_from_confirmation_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, salt=CONFIRM_EMAIL_SALT, max_age=max_age)


def generate_email_change_token(user_id, email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id, "email": email}, salt=EMAIL_CHANGE_SALT)


def get_payload_from_email_change_token(token, max_age=86400):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, salt=EMAIL_CHANGE_SALT, max_age=max_age)


def generate_password_reset_token(user_id):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id}, salt=PASSWORD_RESET_SALT)


def get_payload_from_password_reset_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, salt=PASSWORD_RESET_SALT, max_age=max_age)


def send_email(to_email, subject, body, html_body):
    mail_server = current_app.config.get("MAIL_SERVER")
    mail_username = current_app.config.get("MAIL_USERNAME")
    mail_password = current_app.config.get("MAIL_PASSWORD")

    if not mail_server:
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = current_app.config["MAIL_DEFAULT_SENDER"]
    message["To"] = to_email
    message.set_content(body)
    message.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(mail_server, current_app.config["MAIL_PORT"]) as smtp:
        if current_app.config["MAIL_USE_TLS"]:
            smtp.starttls()
        if mail_username and mail_password:
            smtp.login(mail_username, mail_password)
        smtp.send_message(message)

    return True


def send_signup_confirmation_email(pending_signup):
    token = generate_confirmation_token({"pending_signup_id": pending_signup.id})
    confirmation_url = url_for("main.confirm_email", token=token, _external=True)
    subject = "Confirm your RecipeHub email"
    body, html_body = build_confirmation_email(pending_signup.username, confirmation_url)

    if not send_email(pending_signup.email, subject, body, html_body):
        print(f"Email confirmation link for {pending_signup.email}: {confirmation_url}")

    return confirmation_url


def send_email_change_confirmation(user, new_email):
    token = generate_email_change_token(user.id, new_email)
    confirmation_url = url_for("main.confirm_email_change", token=token, _external=True)
    subject = "Confirm your RecipeHub email change"
    body, html_body = build_email_change_email(user.username, confirmation_url)

    if not send_email(new_email, subject, body, html_body):
        print(f"Email change confirmation link for {new_email}: {confirmation_url}")

    return confirmation_url


def send_password_reset_email(user):
    token = generate_password_reset_token(user.id)
    reset_url = url_for("main.reset_password", token=token, _external=True)
    subject = "Reset your RecipeHub password"
    body, html_body = build_password_reset_email(user.username, reset_url)

    if not send_email(user.email, subject, body, html_body):
        print(f"Password reset link for {user.email}: {reset_url}")

    return reset_url
