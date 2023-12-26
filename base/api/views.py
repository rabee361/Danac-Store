from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, DestroyAPIView ,RetrieveAPIView,UpdateAPIView ,RetrieveUpdateDestroyAPIView, CreateAPIView, GenericAPIView , ListCreateAPIView , RetrieveUpdateAPIView , RetrieveDestroyAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated  ,AllowAny
from rest_framework import status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from base.filters import ProductFilter , PointFilter
import random
from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework.exceptions import NotFound
# from .utils import send_email
from .utils import Utlil
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification

####################################### AUTHENTICATION ###################################################################3#######

class SignUpView(GenericAPIView):
    serializer_class  = SignUpSerializer
    def post(self, request):
        user_information = request.data
        serializer = self.get_serializer(data=user_information)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = CustomUser.objects.get(phonenumber=user_data['phonenumber'])

        device_token = request.data.get('device_token')
        device_type = request.data.get('device_type')
        if device_token:
            FCMDevice.objects.update_or_create(user=user, defaults={'registration_id': device_token ,'type' : device_type})        
    
        token = RefreshToken.for_user(user)
        tokens = {
            'refresh':str(token),
            'accsess':str(token.access_token)
        }
        return Response({'information_user':user_data,'tokens':tokens})






class UserLoginApiView(GenericAPIView):
    """
    An endpoint to authenticate existing users their email and passowrd.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.filter(email = request.data['username']).first()
        if not user:
            user = CustomUser.objects.get(phonenumber = request.data['username'])
        token = RefreshToken.for_user(user)
        data = serializer.data
        data['tokens'] = {'refresh':str(token), 'access':str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)
    

class UpdateImageUserView(APIView):
    def put(self, requset, user_pk):
        user = CustomUser.objects.get(id=user_pk)
        serializer = UpdateUserSerializer(user, data=requset.data, many=False, context={'request':requset})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success':"The changed image Profile has been successfully."},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)



class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny,]
    def put(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        try:
            ver_user = user.codeverification_set.filter(user__id=user_id).first()
            if ver_user.is_verified:
                data = request.data
                serializer = self.get_serializer(data=data, context={'user_id':user_id})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                messages = {
                    'message':'Password Changed Successfully.'
                }
                ver_user.delete()
                return Response(messages, status=status.HTTP_200_OK)
            else:
                return Response({'error':'please verification code'})
        except CodeVerification.DoesNotExist:
            return Response({'message':'ليس لديك صلاحية لتغيير كبمة المرور'})





class users(ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer



class LogoutAPIView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ListInformationUserView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class= CustomUserSerializer
    # permission_classes = [permissions.IsAuthenticated]



class GetPhonenumberView(APIView):
    def post(self, request):
        email = request.data['email']
        try: 
            user = get_object_or_404(CustomUser, email=email)
            existing_code = CodeVerification.objects.filter(user=user).first()
            if existing_code:
                existing_code.delete()

            code_verivecation = random.randint(1000,9999)
            # email_body = 'Hi '+user.username+' Use the code below to verify your email \n'+ str(code_verivecation)
            data= {'to_email':user.email, 'email_subject':'Verify your email','username':user.username, 'code': str(code_verivecation)}
            Utlil.send_eamil(data)
            serializer = CodeVerivecationSerializer(data ={
                'user':user.id,
                'code':code_verivecation,
                'is_verified':False,
                'expires_at' : timezone.now() + timedelta(minutes=10)
            })
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message':'تم ارسال رمز التحقق',
                             'user_id' : user.id})
        except:
            raise serializers.ValidationError({'error':'pleace enter valid email'})


class VerefyCodeView(APIView):
    def post(self, request):
        code = request.data['code']
        code_ver = CodeVerification.objects.filter(code=code).first()
        if code_ver:
            if timezone.now() > code_ver.expires_at:
                return Response({"message":"Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
            code_ver.user.is_verified = True
            code_ver.user.save()
            return Response({"message":"تم التحقق من الرمز", 'user_id':code_ver.user.id},status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError({'message':'الرمز خاطئ, يرجى إعادة إدخال الرمز بشكل صحيح'})




class VerifyCodeToChangePassword(APIView):
    def post(self, request):
        code = request.data['code']
        code_ver = CodeVerification.objects.filter(code=code).first()
        if code_ver:
            if timezone.now() > code_ver.expires_at:
                return Response({"message":"Verification code has expired"}, status=status.HTTP_400_BAD_REQUEST)
            code_ver.is_verified = True
            code_ver.save()
            return Response({"message":"تم التحقق من الرمز", 'user_id':code_ver.user.id},status=status.HTTP_200_OK)
        else:
            raise serializers.ValidationError({'message':'الرمز خاطئ, يرجى إعادة إدخال الرمز بشكل صحيح'})




class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        user = request.user
        x = request.data.get('x')
        y = request.data.get('y')
        if x is None or y is None:
            return Response({"error": "Both 'longitude' and 'latitude' coordinates are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            employee = Employee.objects.get(id=user.id)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        employee.location = Point(float(x), float(y))
        employee.save()

        return Response({"message": "Location updated successfully."}, status=status.HTTP_200_OK)




######################################### CART & PRODUCTS ##########################################################################

class listCreateProducts(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class SpecialProducts(APIView):
    def get(self,request):
        products = Product.objects.all().order_by('?')
        serializer = Product2Serializer(products,many=True,context={'request': request})
        return Response(serializer.data)


class RetUpdDesProduct(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


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
    


class RetUpdDesCategory(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

#################################################### CART HNADLING #####################################################################

# class CartProductsView(ListCreateAPIView):
#     # permission_classes = [IsAuthenticated]
#     queryset = Cart_Products.objects.select_related('products','cart').all()
#     serializer_class = Cart_ProductsSerializer
#     def get_queryset(self):
#         client = Client.objects.get(id=1)
#         return Cart_Products.objects.filter(cart__customer=client)
    



class Cart_Items(APIView):
    def get(self,request,pk):
        products = Cart_Products.objects.filter(cart=pk)
        serializer = Cart_ProductsSerializer(products,many=True, context={'request': request})
        return Response(serializer.data)




class Quantity_Handler(APIView):
    def post(self,request,pk,pk2):
        item = Cart_Products.objects.get(id=pk)
        if pk2 == 'add':
            item.add_item()
            serializer = Cart_ProductsSerializer2(item,many=False)
            return Response(serializer.data)
        else:
            item.sub_item()
            if item.quantity == 0:
                item.delete()

            serializer = Cart_ProductsSerializer2(item,many=False)
        return Response(serializer.data)
            


class Add_to_Cart(APIView):
    def post(self,request,pk,pk2):
        client = Client.objects.get(id=pk2)
        item = Product.objects.get(id=pk)
        cart, created = Cart.objects.get_or_create(customer=client)
        cart_products, created = Cart_Products.objects.get_or_create(products=item, cart=cart)
        if not created:
            Cart_Products.objects.filter(products=item, cart=cart).\
                                    update(quantity=F('quantity') + 1)
            product = Cart_Products.objects.get(products=item, cart=cart)
            serializer = Cart_ProductsSerializer2(product,many=False)
            return Response(serializer.data)
        product = Cart_Products.objects.get(products=item, cart=cart)
        serializer = Cart_ProductsSerializer2(product,many=False)
        return Response(serializer.data)



class Delete_From_Cart(DestroyAPIView):
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_Products


###################################### ORDER HANDLING ############################################################################################


class CreateOrderView(APIView):
    def post(self, request, cart_id):
        delivery_date = request.data.get('delivery_date')
        if not delivery_date:
            return Response({"error": "Delivery date is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, id=cart_id)
        user = CustomUser.objects.get(phonenumber=cart.customer.phonenumber)
        order = cart.create_order(delivery_date)
        devices = FCMDevice.objects.filter(user=user.id)
        devices.send_message(
                message =Message(
                    notification=Notification(
                        title='انشاء طلب',
                        body=f'تم ارسال طلبك بنجاح'
                    ),
                ),
            ) 
        order.save()
        

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
     

class ListOrders(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated,]


class ListSimpleOrders(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = SimpleOrderSerializer


class ListClientOrders(GenericAPIView):
    permission_classes = [IsAuthenticated,]
    serializer_class = OrderSerializer
    def get(self,request):
        user = request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        orders = client.order_set.all()
        serializer = self.get_serializer(orders,many=True)
        return Response(serializer.data,)
        


# class ListDeliveredDriverOutputs(ListAPIView):
#     queryset = Order.objects.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = SimpleOrderSerializer
#     def get_queryset(self,request):
#         user = request.user
#         employee = Employee.objects.get(phonnumber=user.phonenumber)
#         return Output.objects.filter(employee=employee,delivered)
    


# class ListNotDeliveredDriverOutputs(ListAPIView):
#     queryset = Order.objects.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = SimpleOrderSerializer
#     def get_queryset(self,request):
#         user = request.user
#         return super().get_queryset()



class ListDeliveredOrders(APIView):
    def get(self,request):
        orders = Order.objects.filter(delivered=True)
        serializer = SimpleOrderSerializer(orders,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ListNotDeliveredOrders(APIView):
    def get(self,request):
        orders = Order.objects.filter(delivered=False)
        serializer = SimpleOrderSerializer(orders,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class GetOrder(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer2



class TotalClientPointsView(ListAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Points.objects.filter(client__id=client_id)


class ExpiredClientPointsView(ListAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Points.objects.filter(Q(client__id=client_id)&Q(expire_date__lt=timezone.now())).distinct()


class UsedClientPointsView(ListAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Points.objects.filter(Q(client__id=client_id)&Q(is_used=True)).distinct()


class ClientPointsView(ListAPIView):
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Points.objects.filter(Q(client__id=client_id)&Q(is_used=False)&Q(expire_date__gt=timezone.now())).distinct()


######################################  ###########


class SalesEmployee(APIView):
    def get(self,request):
        sales_employees = Employee.objects.filter(Q(truck_num__gt=0) & Q(truck_num__isnull=False))
        serializer = SalesEmployeeSerializer(sales_employees,many=True)
        return Response(serializer.data)


class RetSalesEmployee(RetrieveAPIView):
    queryset = Employee.objects.filter(truck_num__gt=0)
    serializer_class = SalesEmployeeSerializer
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        try:
            employee = queryset.get(pk=self.kwargs['pk'])
        except Employee.DoesNotExist:
            raise NotFound("No sales employee matches the given query.")
        return employee


class ListCreateEmployee(ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesEmployee(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesClient(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


    
class ListCreateClient(ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer







class ListCreateSupplier(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class RetUpdDesClient(RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


########################################### HR ######################################################################

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

class ListCreateExtraExpense(ListCreateAPIView):
    queryset = Extra_Expense.objects.all()
    serializer_class = ExtraExpenseSerializer

class RetUpdDesExtraExpense(RetrieveUpdateDestroyAPIView):
    queryset = Extra_Expense.objects.all()
    serializer_class = ExtraExpenseSerializer

class GetSalaryEmployee(ListAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSalarySerializer
    
class ListCreateSalary(ListCreateAPIView):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer

class RetUpdDesSalary(RetrieveUpdateDestroyAPIView):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer


#######################################################################################################################

######################################## Registry ######################################################################

class GetRegistry(ListAPIView):
    queryset = Registry.objects.all()
    serializer_class = RegistrySerializer

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

class ListCreateDeposite(ListCreateAPIView):
    queryset = Deposite.objects.all()
    serializer_class = DepositeSerializer

class RetUpdDesDeposite(RetrieveUpdateDestroyAPIView):
    queryset = Deposite.objects.all()
    serializer_class = DepositeSerializer

class ListCreateWithDraw(ListCreateAPIView):
    queryset = WithDraw.objects.all()
    serializer_class = WithDrawSerializer

class RetUpdDesWithDraw(RetrieveUpdateDestroyAPIView):
    queryset = WithDraw.objects.all()
    serializer_class = WithDrawSerializer

class ListCreatePayment(ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class RetUpdDesPayment(RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class ListCreateRecievedPayment(ListCreateAPIView):
    queryset = Recieved_Payment.objects.all()
    serializer_class = RecievedPaymentSerializer

class RetUpdDesRecievedPaymnt(RetrieveUpdateDestroyAPIView):
    queryset = Recieved_Payment.objects.all()
    serializer_class = RecievedPaymentSerializer

class ListCreateExpense(ListCreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class RetUpdDesExpense(RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


#####################################################################################################################


# ------------------------------------------DAMAGED & RETURNED PRODUCTS------------------------------------------


class ListCreateRetGoodsSupplier(ListCreateAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer


# class ListCreateRetGoodsSupplier(ListAPIView):
#     queryset = ReturnedGoodsSupplier.objects.all()
#     serializer_class = ReturnedGoodsSupplierSerializer2


class RetUpdDesReturnGoodSupplier(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    # permission_classes = [permissions.IsAuthenticated]    


class ListCreateRetGoodsClient(ListCreateAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer


# class ListRetGoodsClient(ListAPIView):
#     queryset = ReturnedGoodsClient.objects.all()
#     serializer_class = ReturnedGoodsClientSerializer2


class RetUpdDesReturnGoodClient(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer
    # permission_classes = [permissions.IsAuthenticated]

class ListCreateDamagedProduct(ListCreateAPIView):
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer    

class RetUpdDesDamagedProduct(RetrieveUpdateDestroyAPIView):
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer
    # permission_classes = [permissions.IsAuthenticated]









#################################################################### MEDIUM ################################################################# 

class CreateMedium(CreateAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer



class RetDesMedium(RetrieveDestroyAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer



class Add_To_Medium(APIView):
    def post(self, request, medium_id, product_id):
        product = Product.objects.get(id=product_id)
        medium = Medium.objects.get(id=medium_id)
        medium_products, created = Products_Medium.objects.get_or_create(product=product, medium=medium)
        if created:
            medium_products.add_num_item()
            medium_products.total_price = medium_products.total_price_of_item
            medium_products.save()

        pro_med_serializer = ProductsMediumSerializer(medium_products)
        return Response(pro_med_serializer.data, status=status.HTTP_200_OK)



class Medium_Handler(APIView):
    def post(self, request, pk, pk2):
        item = Products_Medium.objects.get(id=pk)
        if pk2 == 'add':
            item.add_item()
            serializer = ProductsMediumSerializer(item,many=False)
            return Response(serializer.data)
        else:
            if item.num_item == 1:
                # item.sub_item()
                item.delete()
            else:
                item.sub_item()
                

            serializer = ProductsMediumSerializer(item,many=False)
        return Response(serializer.data)
    

class GetMediumView(RetrieveAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer


class UpdateProductsMedium(RetrieveUpdateAPIView):
    queryset = Products_Medium.objects.all()
    serializer_class = UpdateProductMediumSerializer


class ListMediumView(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def get(self, request, medium_id):
        mediums = Products_Medium.objects.filter(medium__id=medium_id)
        mediums_serializer = ProductsMediumSerializer(mediums, many=True)
        
        return Response(mediums_serializer.data)
    

class CreateMediumForOrderView(APIView):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        medium = Medium.objects.create()
        order_produdts = Order_Product.objects.filter(order=order)
        for product in order_produdts:
            medium_products = Products_Medium.objects.create(
                product = product.product,
                medium = medium,
                num_item=product.quantity,
                total_price=product.total_price
            )
        return Response(status=status.HTTP_200_OK)
       

 

 ##################################################RECEIPTS ######################################################################
        

class GetOutput(RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2


class ListOutputs(ListAPIView):
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2


class ReceiptOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, medium_id):
        # manual_reciept = request.data
        client_id = request.data['client']
        client = Client.objects.filter(id=client_id).first()
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        output_serializer = OutputSerializer2(data={
            'employee':employee.id,
            "client": client.id,
            "verify_code": request.data['verify_code'],
            "recive_pyement": request.data['recive_pyement'],
            "phonenumber":request.data['phonenumber'], 
            "discount":request.data['discount'],
            "Reclaimed_products": request.data['Reclaimed_products'],
            "previous_depts": request.data['previous_depts'],
            'remaining_amount':request.data['remaining_amount'],
            
        })
        if output_serializer.is_valid():
            output = output_serializer.save()
            products = Products_Medium.objects.filter(medium__id=medium_id)
            for product in products:
                quantity_product = Product.objects.get(id=product.product.id)
                quantity_product.quantity -= product.num_item
                quantity_product.save()

                if quantity_product.quantity < quantity_product.limit_less:
                    user = CustomUser.objects.get(id=request.user.id)
                    devices = FCMDevice.objects.filter(user=user.id)
                    devices.send_message(
                        message=Message(
                            notification=Notification(
                                title='create order',
                                body=f'يرجى الانتباه وصل الحد الأدنى من كمية المنتج إلى أقل من 10{quantity_product.name}'
                            ),
                        ),
                    )

                output_product = Output_Products.objects.create(
                    products = product.product,
                    output = output,
                    quantity = product.num_item,
                    discount = product.discount,
                    total = product.total_price
                )
            products.delete()
            return Response(output_serializer.data)
        return Response(output_serializer.errors)
    



class DeliverOutput(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,output_id):
        user = request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        output = Output.objects.get(id=output_id)
        output.delivered = True
        output.save()

        return Response({'message':'order delivered'})



class ListCreateDeliveryArrived(APIView):
    def post(self, request, pk):
        output = Output.objects.filter(id=pk).first()
        employee = Employee.objects.filter(id=request.data['employee']).first()
        delivery_arrived = DelievaryArrived.objects.create(
            output_receipt=output,
            employee = employee
        )
        del_arr_serializer = DelievaryArrivedSerializer(delivery_arrived, many=False)
        return Response(del_arr_serializer.data)
    
    def get(self, request):
        delivery_arrived = DelievaryArrived.objects.all()
        del_arr_serializer = DelievaryArrivedSerializer(delivery_arrived, many=True)
        # user = CustomUser.objects.get(phonenumber=delivery_arrived.employee.phonenumber)
        # devices = FCMDevice.objects.filter(user=user.id)
        # devices.send_message(
        #     message=Message(
        #         notification=Notification(
        #             title='create order',
        #             body= "لديك طلب توصيل جديد"
        #         ),
        #     ),
        # )
        return Response(del_arr_serializer.data)
    





########################################## INCOMING ####################################### 

class CreateIncomingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, medium_id):
        user = request.user
        supplier = Supplier.objects.get(id=request.data['supplier'])
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        incoming_serializer = IncomingSerializer2(data={
            "employee":employee.id,
            "supplier": supplier.id,
            "agent":request.data['agent'],
            "num_truck":request.data['num_truck'],
            "code_verefy": request.data['code_verefy'],
            "recive_pyement": request.data['recive_pyement'],
            "phonenumber":request.data['phonenumber'], 
            "discount":request.data['discount'],
            "Reclaimed_products": request.data['Reclaimed_products'],
            "previous_depts": request.data['previous_depts'],
            "remaining_amount":request.data['remaining_amount'],
        })
        if incoming_serializer.is_valid():
            incoming = incoming_serializer.save()
            products = Products_Medium.objects.filter(medium__id=medium_id)
            for product in products:
                print(product.id)
                update_quantity =Product.objects.get(id=product.product.id)
                update_quantity.quantity += product.num_item
                update_quantity.save()
                income_product = Incoming_Product.objects.create(
                    product = product.product,
                    incoming = incoming,
                    num_item = product.num_item,
                    total_price = product.total_price,
                )
            products.delete()
            return Response(incoming_serializer.data)
        return Response(incoming_serializer.errors)
    



class GetIncoming(RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer2


class ListIncomings(ListAPIView):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer2



############################### MANUAL RECEIPT #####################################################
    


class CreateManualReceiptView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, medium_id):
        user = request.user
        client = Client.objects.get(id=request.data['client'])
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        manual_receipt_serializer = ManualRecieptSerializer(data={
            "employee":employee.id,
            "client": client.id,
            "verify_code": request.data['verify_code'],
            "phonenumber":request.data['phonenumber'], 
            "recive_payment": request.data['recive_payment'],
            "discount":request.data['discount'],
            "reclaimed_products": request.data['reclaimed_products'],
            "previous_depts": request.data['previous_depts'],
            "remaining_amount":request.data['remaining_amount'],
        })
        if manual_receipt_serializer.is_valid():
            manual_receipt = manual_receipt_serializer.save()
            products = Products_Medium.objects.filter(medium__id=medium_id)
            for product in products:
                update_quantity =Product.objects.get(id=product.product.id)
                update_quantity.quantity -= product.num_item
                update_quantity.save()
                if update_quantity.quantity < update_quantity.limit_less:
                    user = CustomUser.objects.get(id=request.user.id)
                    devices = FCMDevice.objects.filter(user=user.id)
                    devices.send_message(
                        message=Message(
                            notification=Notification(
                                title='create order',
                                body=f'يرجى الانتباه وصل الحد الأدنى من كمية المنتج إلى أقل من 10{update_quantity.name}'
                            ),
                        ),
                    )
                    manual_eceipt_products = ManualReceipt_Products.objects.create(
                        product = product.product,
                        manualreceipt = manual_receipt,
                        num_item = product.num_item,
                        discount=product.discount,
                        total_price = product.total_price,
                    )
            products.delete()
            return Response(manual_receipt_serializer.data)
        return Response(manual_receipt_serializer.errors)
    

class GetManualReceipt(RetrieveAPIView):
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer2



class ListManualReceipt(ListAPIView):
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer2









class CreateMediumTwo(ListCreateAPIView):
    queryset = MediumTwo.objects.all()
    serializer_class = MediumTwoSerializer
    # permission_classes = [permissions.IsAuthenticated]

class DesMediumTwo(DestroyAPIView):
    queryset = MediumTwo_Products.objects.all()
    serializer_class = MediumTwo_ProductsSerializer
    # permission_classe = [permissions.IsAuthenticated]


class ListProductsMediumTwo(ListAPIView):
    queryset = MediumTwo_Products.objects.all()
    serializer_class = MediumTwo_ProductsSerializer


class AddToMediumTwo(APIView):
    def post(self, request, mediumtwo_id, product_id):
        medium_two = MediumTwo.objects.get(id=mediumtwo_id)
        product = Product.objects.get(id = product_id)
        mediumtwo_products, created = MediumTwo_Products.objects.get_or_create(
            product = product,
            mediumtwo= medium_two,
        )
        if created:
            mediumtwo_products.quantity=1
            mediumtwo_products.save()
        mediumtwo_serializer = MediumTwo_ProductsSerializer(mediumtwo_products)
        return Response(mediumtwo_serializer.data, status=status.HTTP_201_CREATED)
    



class DeleteMediumTwo(DestroyAPIView):
    queryset = MediumTwo.objects.all()
    serializer_class = MediumTwoSerializer



class MediumTow_Handler(APIView):
    def post(self, request, mediumtwo_id, pk2):
        item = MediumTwo_Products.objects.get(id=mediumtwo_id)
        if pk2 == 'add':
            item.add_item()
            serializer = MediumTwo_ProductsSerializer(item,many=False)
            return Response(serializer.data)
        else:
            if item.quantity == 1:
                item.delete()
            else:
                item.sub_item()
            serializer = MediumTwo_ProductsSerializer(item,many=False)
        return Response(serializer.data)
    
class CreateOrderEnvoyView(APIView):

    def post(self, request, mediumtwo_id):
        mediumtwo = MediumTwo_Products.objects.filter(mediumtwo__id = mediumtwo_id)
        order_envoy_ser = OrderEnvoySerializer(data={
            'client':request.data['client'],
            'phonenumber': request.data['phonenumber'],
            'delivery_date':request.data['delivery_date']
        })
        if order_envoy_ser.is_valid():
            order_envoy = order_envoy_ser.save()
            for medium in mediumtwo:
                product_order_envoy = Product_Order_Envoy.objects.create(
                    order_envoy = order_envoy,
                    product = medium.product,   
                )

                order_envoy.products_num += medium.quantity
                order_envoy.total_price += (medium.quantity * medium.product.sale_price)
                order_envoy.save()
            MediumTwo.objects.get(id=mediumtwo_id).delete()
            return Response(order_envoy_ser.data, status=status.HTTP_201_CREATED)
        return Response(order_envoy_ser.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListOrderEnvoy(APIView):

    def get(self, request, pk):
        order_envoy = OrderEnvoy.objects.get(id=pk)
        serializer = ListOrderEnvoySerialzier(order_envoy, many=False)
        product_order_envoy = Product_Order_Envoy.objects.filter(order_envoy__id = pk)
        serializer_two = ProductOrderEnvoySerializer(product_order_envoy, many=True)

        return Response({
            'order_envoy':serializer.data,
            'products_order_envoy':serializer_two.data
        })
    


