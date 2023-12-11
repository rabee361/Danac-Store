from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated  ,AllowAny



class StudentSignupView(CreateAPIView):
    serializer_class = UserSerializer



class test(ListAPIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        return Response(request.data)
    



class CurrentUserView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)


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
