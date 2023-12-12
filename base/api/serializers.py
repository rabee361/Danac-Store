from rest_framework import serializers
from base.models import *
from django.contrib.auth import login
from django.contrib.auth.password_validation import validate_password


class signupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=CustomUser
        fields = ['phonenumber','username', 'password']

    def save(self, **kwargs):
        user = CustomUser(
            phonenumber=self.validated_data['phonenumber'],
            username = self.validated_data['username']
        )
        password = self.validated_data['password']
        user.set_password(password)
        user.is_active = False
        user.save()
    
        return user
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

    def validate(self, data):
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        user.is_active = False
        user.save()
        return user



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'





class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


    
