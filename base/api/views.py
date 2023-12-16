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
from base.filters import ProductFilter , ProductFilterName
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



class ListCreateEmployee(ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class RetUpdDesEmployee(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

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
    


class CartView(ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer



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

class ListCreateBonus(ListCreateAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer

class RetUpdDesBonusView(RetrieveUpdateDestroyAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer

class ListCreateDicountView(ListCreateAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class RetUpdDesDicountView(RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class ListCreateAdvanceView(ListCreateAPIView):
    queryset = Advance_On_salary.objects.all()
    serializer_class = Advance_on_SalarySerializer

class RetUpdDesAdvanceView(RetrieveUpdateDestroyAPIView):
    queryset = Advance_On_salary.objects.all()
    serializer_class = Advance_on_SalarySerializer

class ListCreateExpense(ListCreateAPIView):
    queryset = Extra_Expense.objects.all()
    serializer_class = ExpenseSerializer

class RetUpdDesExpense(RetrieveUpdateDestroyAPIView):
    queryset = Extra_Expense.objects.all()
    serializer_class = ExpenseSerializer


class RetUpdDelDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer




class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        client = Client.objects.get(phomnenumber=user.phonenumber)
        cart = Cart.objects.get(customer=client)
        cart_products = Cart_Products.objects.filter(cart=cart)
        products_name = []
        quantity = 0
        for cart_product in cart_products:
            quantity +=cart_product.quantity
            products_name.append(cart_product.products.name)
            cart_product.delete()
        print(products_name)
        print(quantity)

        order_serializer = OrderSerializer(data= {
            'clinet':client.id,
            'products':products_name,
            'total':quantity,
            'delivery_date':request.data['date']
        })
        if order_serializer.is_valid():
            order_serializer.save()

            return Response(order_serializer.data)
        return Response(order_serializer.errors)
        

class ListOrdersUserView(GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        user = request.user
        client = Client.objects.get(phomnenumber=user.phonenumber)
        orders = client.order_set.all()
        serializer = self.get_serializer(orders, many=True)
        response = serializer.data

        return Response(response)




class ListCreateManualRecieptView(APIView):

    def post(self, request):
        manual_reciept = request.data
        manual_reciept_serializer = ManualRecieptSerializer(data=manual_reciept)
        if manual_reciept_serializer.is_valid():
            manuals_reciept = manual_reciept_serializer.save()
            manual_products = request.data['products']
            for manual_product in manual_products:
                manual_product['manualreciept'] = manuals_reciept.id
                manualrecieptser = ManualRecieptProductsSerializer(data=manual_product)
                if manualrecieptser.is_valid():
                    manualrecieptser.save()
                else:

                    return Response(manual_reciept_serializer.errors)
            return Response(manual_reciept_serializer.data)
        return Response(manual_reciept_serializer.errors)
    
    def get(self, request):
        manualreciepts = ManualReciept.objects.all()
        serializer = ManualRecieptSerializer(manualreciepts, many=True)
        data = serializer.data

        return Response(data)
    


class ListManualRecieptProductsView(ListAPIView):
    queryset = ManualReciept_Products.objects.all()
    serializer_class = ManualRecieptProductsSerializer



class SearchView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilterName
