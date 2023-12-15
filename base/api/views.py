from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView ,RetrieveUpdateDestroyAPIView, CreateAPIView, GenericAPIView , ListCreateAPIView
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



class SignUpView(GenericAPIView):
    serializer_class  = SignUpSerializer
    def post(self, request):
        user_information = request.data
        serializer = self.get_serializer(data=user_information)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = CustomUser.objects.get(phonenumber=user_data['phonenumber'])
        token = RefreshToken.for_user(user)
        tokens = {
            'refresh':str(token),
            'accsess':str(token.access_token)
        }
        return Response({'information_user':user_data,'tokens':tokens})




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
    



class listCreateProducts(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter



class ListCreateCategory(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"message": "تمت الإضافة بنجاح"},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




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



class ListCreateClient(ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class RetrieveClient(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


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
        



class ListCreateOrder(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class CreateOrder(APIView):
    def post(self,request):
        i = request.data
        serializer = OrderSerializer(data=i)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response("bad")




class ListIncomings(ListCreateAPIView):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer



class CreateIncomingView(APIView):
    def post(self, request, format=None):
        incoming_data = request.data
        incoming_serializer = IncomingSerializer(data=incoming_data)
        if incoming_serializer.is_valid():
            incoming = incoming_serializer.save()
            products_data = incoming_data.get('products', [])
            for product_data in products_data:
                product_data['incoming'] = incoming.id
                product_serializer = IncomingProductSerializer(data=product_data)
                if product_serializer.is_valid():
                    product_serializer.save()
                else:
                    return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(incoming_serializer.data, status=status.HTTP_201_CREATED)
        return Response(incoming_serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CreateIncomingProducts(ListCreateAPIView):
    queryset = Incoming_Products.objects.all()
    serializer_class = IncomingProductSerializer





# class ListClients(ListAPIView)
# class getClients
# class createClientView()


class ListCreateSupplier(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer





class ListCreatEmployeeView(ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class RetUpdDesEmployeeAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ListCreatOverTimeView(ListCreateAPIView):
    queryset = OverTime.objects.all()
    serializer_class = OverTimeSerializer

class RetUpdDesOverTimeView(RetrieveUpdateDestroyAPIView):
    queryset = OverTime.objects.all()
    serializer_class = OverTimeSerializer

class ListCreateAbsenceView(ListCreateAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class RetUpdDesAbsenceAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class ListCreateAwardView(ListCreateAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer

class RetUpdDesAwardView(RetrieveUpdateDestroyAPIView):
    queryset = Award.objects.all()
    serializer_class = AwardSerializer

class ListCreateDicountView(ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class RetUpdDesDicountView(RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

# class ListCreateAdvanceView(ListCreateAPIView):
#     queryset = Advance.objects.all()
#     serializer_class = AdvanceSerializer

# class RetUpdDesAdvanceView(RetrieveUpdateDestroyAPIView):
#     queryset = Advance.objects.all()
#     serializer_class = AdvanceSerializer

# class ListCreateExpenceView(ListCreateAPIView):
#     queryset = Expense.objects.all()
#     serializer_class = ExpenseSerializer

# class RetUpdDesExpenceView(RetrieveUpdateDestroyAPIView):
#     queryset = Expense.objects.all()
#     serializer_class = ExpenseSerializer



# class addToCart
# class listCart
