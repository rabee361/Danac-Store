from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView
from .validation import custom_validation
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



class SignupView(CreateAPIView):
    """
    An endpoint for the client to create a new Student.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    # def perform_create(self, serializer):
    #     user = serializer.save()
    #     token = RefreshToken.for_user(user)
    #     data_user = serializer.data
    #     data_user['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
    #     self.headers = {"user": data_user, "message":"account created successfully"}

    def post(self, request, *args, **kwargs):
        # clean_data = custom_validation(request.data)
        serializer = self.get_serializer(data=request.data)   
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = CustomUser.objects.get(phonenumber=user_data['phonenumber'])
        token = RefreshToken.for_user(user)
        user_data['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
        return Response(
            {
                "user": user_data,
                "message":"account created successfully"
            })


class test(ListAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        return Response("hi")

class LogoutAPIView(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

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
