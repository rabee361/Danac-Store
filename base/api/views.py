from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken


class StudentSignupView(GenericAPIView):

    """
    An endpoint for the client to create a new Student.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = signupSerializer

    def post(self, request, *args, **kwargs):
        clean_data = custom_validation(request.data)
        serializer = self.get_serializer(data=clean_data)   
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = CustomUser.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user)
        data_user = serializer.data
        data_user['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
        return Response(
            {
                "user": data_user,
                "message":"account created successfully"
            })





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
