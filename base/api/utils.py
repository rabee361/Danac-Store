from django.core.mail import EmailMessage

class Utlil:
    @staticmethod
    def send_eamil(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()
