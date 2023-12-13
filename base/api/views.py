from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .validation import custom_validation
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from base.filter import ProductFilter
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import random



class SignupView(CreateAPIView):
    """
    An endpoint for the client to create a new Student.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = SignUpSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data_user = serializer.data
        data_user['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
        self.headers = {"user": data_user, "message":"account created successfully"}



    # def post(self, request, *args, **kwargs):
    #     # clean_data = custom_validation(request.data)
    #     serializer = self.get_serializer(data=request.data)   
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     user_data = serializer.data
    #     user = CustomUser.objects.get(phonenumber=user_data['phonenumber'])
    #     token = RefreshToken.for_user(user)
    #     user_data['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
    #     return Response(
    #         {
    #             "user": user_data,
    #             "message":"account created successfully"
    #         })

class UserLoginApiView(GenericAPIView):
    """
    An endpoint to authenticate existing users their email and passowrd.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserLoginSerilizer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(phonenumber = request.data['phonenumber'])
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {'refresh':str(token), 'access':str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        messages = {
            'message':'Password Changed Successfully.'
        }
        return Response(messages, status=status.HTTP_200_OK)

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

class GetPhonenumberView(APIView):
    # serializer_class = CustomUserSerializer

    def post(self, request):
        phonenumber = request.data['phonenumber']

        try: 
            user = get_object_or_404(CustomUser, phonenumber=phonenumber)
            existing_code = CodeVerivecation.objects.filter(user=user).first()
            if existing_code:
                existing_code.delete()

            code_verivecation = random.randint(1000,9999)
            serializer = CodeVerivecationSerializer(data ={
                'user':user.id,
                'code':code_verivecation
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':'تم ارسال رمز التحقق'})
        except:
            raise serializers.ValidationError({'error':'pleace enter valid phone number'})

class sendCodeView(APIView):
    def post(self, request):
        code = request.data['code']

        code_ver = CodeVerivecation.objects.filter(code=code).first()
        if code_ver:
            return Response(status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError({'message':'الرمز خاطئ, يرجى إعادة إدخال الرمز بشكل صحيح'})

class ListCreatCategoryView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# class retrieveUpdateDestroyCategoryView(RetrieveUpdateDestroyAPIView):


class ListCreateProductView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

class GetProductView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UserListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)


    # def get(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)


class CreateCartProductsView(ListCreatCategoryView):
    pass

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
