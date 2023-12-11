from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



class StudentSignupView(CreateAPIView):
    """
    An endpoint for the client to create a new Student.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data_user = serializer.data
        data_user['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
        self.headers = {"user": data_user, "message":"account created successfully"}



class test(ListAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        return Response("hi")
    
# class ListClients(ListAPIView)
# class getClients
# class createClientView()


# class listSupplier
# class getSupplier
# class createSupplier


# class createProduct
# class getProduct
# class listProduct


# class addToCart
# class listCart
