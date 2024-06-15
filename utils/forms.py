from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from base.models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ('phonenumber','email')
    
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('phonenumber','email')