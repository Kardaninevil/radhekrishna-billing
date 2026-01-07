import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "yourgmail@gmail.com"
EMAIL_PASSWORD = "your_app_password"


def send_reset_email(to_email: str, token: str):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset - Radhekrishna Engineering Billing"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    msg.set_content(
        f"Use this token to reset your password:\n\n{token}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
