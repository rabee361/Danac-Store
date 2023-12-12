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
    
# class userSerializers(serializers.ModelSerializer):
#     code = serializers.IntegerField()

#     class Meta:
#         model = CustomUser
#         fieldes = 