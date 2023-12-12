from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView , ListCreateAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated  ,AllowAny
from rest_framework import status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from base.filters import ProductFilter
import random
from django.shortcuts import get_object_or_404

class SignupView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response



class test(ListAPIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        return Response(request.data)



class CurrentUserView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)




class listProducts(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter



class ListCategory(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GetProduct(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class LogoutAPIView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)




class UserLoginApiView(GenericAPIView):
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
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        messages = {
            'message':'Password Changed Successfully.'
        }
        return Response(messages, status=status.HTTP_200_OK)



class CartProducts(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_ProductsSerializer

    def get_queryset(self):
        client = Client.objects.get(id=1)
        return Cart_Products.objects.filter(cart__customer=client)
    
class GetPhonenumberView(APIView):    
    def post(self, request):
        phonenumber = request.data['phonenumber']
        if phonenumber is None:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_object_or_404(CustomUser, phonenumber=phonenumber)
            print(user)
            existing_code = CodeVerification.objects.filter(user=user).first()

            if existing_code:
                existing_code.delete()

            code_verification = random.randint(1000,9999)
            code = CodeVerification.objects.create(user=user, code=code_verification)
            serializer = CodeSerializer(code)
            return Response({'message':'تم ارسال رمز التحقق', 'data': serializer.data})
        except:
            raise serializers.ValidationError({'error':'Please enter a valid phone number'})
# class QuantityHandlerView(APIView):
#     def post(self, request, pk, pk2):
#         item = Cart_Products.objects.get(id=pk)
#         if pk2 == 'add':
#             item.add_item()
#         elif pk2 == 'subtract':
#             if item.quantity == 1:
#                 item.sub_item()
#                 item.delete()
#             else:
#                 item.sub_item()
#         else:
#             return Response({"error": "Invalid operation"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"success": "Operation performed successfully"}, status=status.HTTP_200_OK)


# def remove_from_cart(request , pk):
#     item = Cart_Products.objects.get(id=pk)
#     item.delete()
#     return redirect(request.META.get('HTTP_REFERER'))


# def add_to_cart(request,pk):
#     item = Product.objects.get(id=pk)
#     cart, created = Cart.objects.get_or_create(customer=request.user)
#     cart_products, created = Cart_Products.objects.get_or_create(products=item, cart=cart)
#     if not created:
#         Cart_Products.objects.filter(products=item, cart=cart).\
#                                 update(quantity=F('quantity') + 1)
#     return redirect(request.META.get('HTTP_REFERER'))


# class ListClients(ListAPIView)
# class getClients
# class createClientView()


# class listSupplier
# class getSupplier
# class createSupplier



# class addToCart
# class listCart
