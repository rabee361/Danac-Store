from django.core.mail import EmailMessage
from django.template.loader import render_to_string

class Utlil:
    @staticmethod
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