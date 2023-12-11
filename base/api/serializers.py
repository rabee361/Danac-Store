from rest_framework import serializers
from base.models import *


class signupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields = ['phonenumber','username', 'password']
        extra_kwargs = {
            'password':{'write_only':True,}
        }

    # def validate(self, attrs):
    #     eamil = attrs.get('email', '')
    #     username = attrs.get('username', '')

    #     if not username.isalnum:
    #         raise serializers.ValidationError('The username should only contain alphanumeric characters')
    #     return attrs

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)

    # def save(self, **kwargs):
    #     user = CustomUser(
    #         username=self.validated_data['username'],
    #         email = self.validated_data['email']
    #     )
    #     password = self.validated_data['password']
    #     user.set_password(password)
    #     user.save()
    #     # Student.objects.create(user=user)
    #     return user



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['phonenumber','username', 'password']

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        return repr['username','phonenumber']



class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

    # def save(self, **kwargs):
    #     user = CustomUser(
    #         phonenumber=self.validated_data['phonenumber'],
    #         username = self.validated_data['username']
    #     )
    #     password = self.validated_data['password']
    #     user.set_password(password)
    #     user.is_active = False
    #     user.save()
    #     return user
    
