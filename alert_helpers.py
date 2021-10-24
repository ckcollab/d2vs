import os
import smtplib

from email.message import EmailMessage
from threading import Thread

from dotenv import load_dotenv


# For sending pickit alerts...
load_dotenv()

GOOGLE_EMAIL_USERNAME = os.environ.get('GOOGLE_EMAIL_USERNAME')
GOOGLE_EMAIL_PASSWORD = os.environ.get('GOOGLE_EMAIL_PASSWORD')


def send_mail(subject, body):
    def _inner():
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = GOOGLE_EMAIL_USERNAME
        msg['To'] = GOOGLE_EMAIL_USERNAME
        msg.set_content(body)

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GOOGLE_EMAIL_USERNAME, GOOGLE_EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

    thread = Thread(target=_inner)
    thread.start()  # run in background, may fail, may not! who cares keep looting!
