import random
from datetime import timedelta
import string
from django.utils import timezone


def get_expiration_time():
    return timezone.now() + timedelta(minutes=10)

def get_expiration_date():
    return timezone.now() + timedelta(days=30)

def generate_barcode():
    characters = string.ascii_letters + string.digits
    code = ''.join(random.choice(characters) for _ in range(8))
    return code
