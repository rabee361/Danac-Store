import random
from datetime import timedelta
import string
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def get_expiration_time():
    return timezone.now() + timedelta(minutes=10)

def get_expiration_date():
    return timezone.now() + timedelta(days=30)

def generate_barcode():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(8))
    return code

def send_email(data):
    email_body = render_to_string('email_template.html', {'username': data['username'], 'code': data['code']})
    email = EmailMessage(subject=data['email_subject'], body=email_body, to=[data['to_email']])
    email.content_subtype = 'html'
    email.send()

def send_email2(data):
    email_body = render_to_string('Account_Refused.html', {'username': data['username']})
    email = EmailMessage(subject=data['email_subject'], body=email_body, to=[data['to_email']])
    email.content_subtype = 'html'
    email.send()