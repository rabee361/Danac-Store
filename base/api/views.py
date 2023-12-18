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
from django.db.models import F


######--------- authentication --------#######

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



class LogoutAPIView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



#####-----testing-----#####
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


############-------cart and products -----######################
    
class ListCreateClient(ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


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
    

class RetUpdDesProduct(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

############################ CART HNADLING ######################
        
class CartProductsView(ListAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Cart_Products.objects.select_related('products','cart').all()
    serializer_class = Cart_ProductsSerializer

    def get_queryset(self):
        client = Client.objects.get(id=1)
        return Cart_Products.objects.filter(cart__customer=client)
    

class CartView(ListAPIView):
    queryset = Cart.objects.select_related('customer').prefetch_related('items').all()
    serializer_class = CartSerializer


class Quantity_Handler(APIView):
    def post(self,request,pk,pk2):
        item = Cart_Products.objects.get(id=pk)
        if pk2 == 'add':
            item.add_item()
            serializer = Cart_ProductsSerializer(item,many=False)
            return Response(serializer.data)
        else:
            item.sub_item()
            if item.quantity == 1:
                item.delete()
            serializer = Cart_ProductsSerializer(item,many=False)
        return Response(serializer.data)
            


class Add_to_Cart(APIView):
    def post(self,request,pk,pk2):
        client = Client.objects.get(id=pk2)
        item = Product.objects.get(id=pk)
        cart, created = Cart.objects.get_or_create(customer=client.id)
        cart_products, created = Cart_Products.objects.get_or_create(products=item, cart=cart)
        if not created:
            Cart_Products.objects.filter(products=item, cart=cart).\
                                    update(quantity=F('quantity') + 1)

            return Response("added to cart")
        serializer = Cart_ProductsSerializer(cart_products)
        return Response("تمت اضافة المنتج الى السلة")

##################### END CART ######################

##################### ORDER HANDLING ####################


class CreateOrderView(APIView):
    def post(self, request, cart_id):
        delivery_date = request.data.get('delivery_date')
        if not delivery_date:
            return Response({"error": "Delivery date is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, id=cart_id)
        order = cart.create_order(delivery_date)
        order.save()

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
     

class ListOrders(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated,]




################---------- -----------############

class ListCreateEmployee(ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesEmployee(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesClient(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer





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



###############----------- HR -------############

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




class ListCreateClientDebts(ListCreateAPIView):
    queryset = Debt_Client.objects.all()
    serializer_class = Client_DebtSerializer


class ListCreateSupplierDebts(ListCreateAPIView):
    queryset = Debt_Supplier.objects.all()
    serializer_class = Supplier_DebtSerializer

class RetUpdDesSupplierDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt_Supplier.objects.all()
    serializer_class = Supplier_DebtSerializer


class RetUpdDesClientDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt_Client.objects.all()
    serializer_class = Client_DebtSerializer


