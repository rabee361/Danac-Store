from rest_framework.serializers import ValidationError
from django.contrib.auth import get_user_model

UserModel = get_user_model()

def custom_validation(data):
    phonenumber = data['phonenumber']
    username = data['username'].strip()
    password = data['password'].strip()
    
    if not phonenumber:
        raise ValidationError({"error_message":"The field phonenumber is required."})
    
    if not username:
        raise ValidationError({"error_message":"The username is required for registration."})
    
    if not password:
        raise ValidationError({"error_message":"The field passowrd is required."})
    

    