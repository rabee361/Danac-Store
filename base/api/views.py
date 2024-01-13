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
from base.filters import ProductFilter ,SalaryFilter
import random
from django.shortcuts import get_object_or_404
from django.db.models import F
from rest_framework.exceptions import NotFound
# from .utils import send_email
from .utils import Utlil
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification
from .permissions import *


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
        data['image'] = request.build_absolute_uri(user.image.url)
        data['id'] = user.id
        data['tokens'] = {'refresh':str(token), 'access':str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)
    

class UpdateImageUserView(APIView):
    def put(self, requset, user_pk):
        user = CustomUser.objects.get(id=user_pk)
        serializer = UpdateUserSerializer(user, data=requset.data, many=False, context={'request':requset})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success':"The changed image Profile has been successfully.",
                 'image' : serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)




class GetNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notification = Notifications.objects.filter(user__id=user.id)
        serializer = SerializerNotificationI(notification, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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




class LogoutAPIView(GenericAPIView):
    serializer_class = UserLogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)



class ListInformationUserView(RetrieveAPIView):
    [IsAuthenticated]
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
            Utlil.send_email(data)
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
            employee = Employee.objects.get(phonenumber=user.phonenumber)
        except Employee.DoesNotExist:
            return Response({"error": "Employee not found."}, status=status.HTTP_404_NOT_FOUND)
        employee.location = Point(float(x), float(y))
        employee.save()

        return Response({"message": "Location updated successfully.",
                         "longitude" : employee.location.x ,
                         "latitude" : employee.location.y}, status=status.HTTP_200_OK)



class GetSalesEmployeeLocation(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,employee_id):
        employee = Employee.objects.get(id=employee_id)
        serializer = SalesEmployeeLocationSerializer(employee,many=False)

        return Response(serializer.data,status=status.HTTP_200_OK)





######################################### CART & PRODUCTS ##########################################################################

class listCreateProducts(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class SpecialProducts(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        products = Product.objects.all().order_by('?')
        serializer = Product2Serializer(products,many=True,context={'request': request})
        return Response(serializer.data)


class RetUpdDesProduct(RetrieveUpdateDestroyAPIView):
    [IsAuthenticated,Is_Client]
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
    permission_classes = [IsAuthenticated]
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
    pagination_class = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

#################################################### CART HNADLING #####################################################################

class Cart_Items(APIView):
    permission_classes = [IsAuthenticated,Is_Client]
    def get(self,request,pk):
        products = Cart_Products.objects.filter(cart=pk)
        serializer = Cart_ProductsSerializer(products,many=True, context={'request': request})
        return Response(serializer.data)




class Quantity_Handler(APIView):
    permission_classes = [IsAuthenticated,Is_Client]
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
    permission_classes = [IsAuthenticated,Is_Client]
    def post(self,request,pk,pk2):
        user = CustomUser.objects.get(id=pk2)
        client = Client.objects.get(phonenumber=user.phonenumber)
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
    permission_classes = [IsAuthenticated,Is_Client]
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_Products


###################################### ORDER HANDLING ############################################################################################


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated,Is_Client]
    def post(self, request, cart_id):
        delivery_date = request.data.get('delivery_date')
        if not delivery_date:
            return Response({"error": "Delivery date is required"}, status=status.HTTP_400_BAD_REQUEST)
        cart = get_object_or_404(Cart, id=cart_id)
        order = cart.create_order(delivery_date)
        ###################################
        user = CustomUser.objects.get(phonenumber=cart.customer.phonenumber)
        devices = FCMDevice.objects.filter(user=user.id)
        title = 'انشاء طلب'
        body = f'تم ارسال طلبك بنجاح'
        devices.send_message(
                message =Message(
                    notification=Notification(
                        title=title,
                        body=body
                    ),
                ),
            )
        Notifications.objects.create(user=user,body=body,title=title)
        ###################################
        order.save()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
     

class ListOrders(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    # permission_classes = [permissions.IsAuthenticated,]


class GetOrder(RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer2



class ListSimpleOrders(ListAPIView):
    queryset = Order.objects.all()
    serializer_class = SimpleOrderSerializer


class ListClientOrders(GenericAPIView):
    permission_classes = [IsAuthenticated,Is_Client]
    serializer_class = OrderSerializer
    def get(self,request):
        user = request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        orders = client.order_set.all()
        serializer = self.get_serializer(orders,many=True)
        return Response(serializer.data,)
        

class DeleteOrder(DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


######################################Delivery Arrived ##########################################################3
    

class DelevaryArrivedForEmployee(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, state):
        user = request.user             
        delevary_arrived = DelievaryArrived.objects.filter(employee__phonenumber= user.phonenumber, is_delivered=state)
        serializer = DelevaryArrivedSerializer(delevary_arrived, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetDelevaryArrivedForEmployee(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        delevary_arrived = DelievaryArrived.objects.filter(id=pk).first()
        serializer = DelevaryArrivedSerializer(delevary_arrived, many=False)
        output = Output.objects.filter(id=delevary_arrived.output_receipt.id).first()
        print(output.id)
        products = Output_Products.objects.filter(output__id= output.id)
        products_serializer = ProductsOutputSerializer(products, many=True)
        receipt_serializer = OutputSerializer(output)
        return Response({'receipt':receipt_serializer.data, 'products':products_serializer.data , 'is_delivered':serializer.data['is_delivered']})
    

class AcceptDelevaryArrived(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        delevary_arrived = DelievaryArrived.objects.filter(id=pk).first()
        delevary_arrived.is_delivered = request.data['state']
        delevary_arrived.save()
        return Response(status=status.HTTP_200_OK)
    





class TotalClientPointsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        return Points.objects.filter(client=client)


class ExpiredClientPointsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        return Points.objects.filter(Q(client=client)&Q(expire_date__lt=timezone.now())).distinct()


class UsedClientPointsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        return Points.objects.filter(Q(client=client)&Q(is_used=True)).distinct()


class ClientPointsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Points.objects.all()
    serializer_class = PointsSerializer
    def get_queryset(self):
        user = self.request.user
        client = Client.objects.get(phonenumber=user.phonenumber)
        return Points.objects.filter(Q(client=client)&Q(is_used=False)&Q(expire_date__gt=timezone.now())).distinct()


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

class GetSalaryEmployee(RetrieveAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSalarySerializer
    
class ListCreateSalary(ListCreateAPIView):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = SalaryFilter
    def perform_create(self, serializer):
        serializer.save(hr=self.request.user)

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

    def perform_destroy(self, instance):
        supplier = instance.supplier_name
        supplier.debts -= instance.amount
        supplier.save()
        instance.delete()

class RetUpdDesClientDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt_Client.objects.all()
    serializer_class = Client_DebtSerializer

    def perform_destroy(self, instance):
        client = instance.client_name
        client.debts -= instance.amount
        client.save()
        instance.delete()


class GetClientDebt(APIView):
    def get(self,request,pk):
        try:
            client = Client.objects.get(id=pk)
            serializer = ClientSerializer(client,many=False)
            return Response({
                "client" : pk ,
                "client_debt":serializer.data['debts']})
        except:
            return Response({"error": "No Cliet with that id"})


class GetSupplierDebt(APIView):
    def get(self,request,pk):
        try:
            supplier = Supplier.objects.get(id=pk)
            serializer = SupplierSerializer(supplier,many=False)
            return Response({
                "supplier" : pk,
                "supplier_debt":serializer.data['debts']})
        except:
            return Response({"error": "No Supplier with that id"})   
    


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
        serializer = MediumSerializer(medium,many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)
       
class DeleteProductsMediumView(RetrieveDestroyAPIView):
    queryset = Products_Medium.objects.all()
    serializer_class = ProductsMediumSerializer
 

 ##################################################RECEIPTS ######################################################################
        

class GetOutput(RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2

    def get_serializer_context(self):
        return {'show_datetime': True}

class ListOutputs(ListAPIView):
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}


class UpdateOutputReceipt(RetrieveUpdateDestroyAPIView):
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2

class RetUpdDesOutputProduct(RetrieveUpdateDestroyAPIView):
    queryset = Output_Products.objects.all()
    serializer_class = ProductsOutputSerializer2

    def perform_destroy(self, instance):
        product = instance.product
        product.quantity += instance.quantity
        product.save()
        instance.delete()

class CreateOutputProduct(CreateAPIView):
    queryset = Output_Products.objects.all()
    serializer_class = ProductsOutputSerializer2


class ReceiptOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, medium_id):
        output_serializer = OutputSerializer2(data=request.data, context={'request': request})
        if output_serializer.is_valid():
            total_points = 0
            output = output_serializer.save()
            products = Products_Medium.objects.filter(medium__id=medium_id)
            for product in products:
                quantity_product = Product.objects.get(id=product.product.id)
                quantity_product.quantity -= product.num_item
                quantity_product.save()
    #############################################################################
                if quantity_product.quantity < quantity_product.limit_less:
                    user = CustomUser.objects.get(id=request.user.id)
                    devices = FCMDevice.objects.filter(user=user.id)
                    title = 'نقص كمية منتج'
                    body = f'نقص كمية المنتج {quantity_product.name}{quantity_product.limit_less}عن الحد الأدنى'
                    devices.send_message(
                        message=Message(
                            notification=Notification(
                                title=title,
                                body=body
                            ),
                        ),
                    )
                    Notifications.objects.create(
                        user = user,
                        title = title,
                        body = body
                    )
########################################################################################
                output_product = Output_Products.objects.create(
                    product = product.product,
                    output = output,
                    quantity = product.num_item,
                    total_price = product.total_price
                )
                total_points += output_product.product_points
            client_points = Points.objects.create(
                client = output.client,
                number = total_points
            )
            products.delete()
            medium = Medium.objects.get(id=medium_id)
            medium.delete()
            return Response(output_serializer.data)
        return Response(output_serializer.errors,status=status.HTTP_400_BAD_REQUEST)







class DelevaryArrivedForEmployee(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, state):
        user = request.user
        delevary_arrived = DelievaryArrived.objects.filter(employee__phonenumber= user.phonenumber, is_delivered=state)
        serializer = DelevaryArrivedSerializer(delevary_arrived, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ListCreateDeliveryArrived(APIView):
    def post(self, request, pk):
        # Check if a DelievaryArrived with the given output already exists
        if DelievaryArrived.objects.filter(output_receipt_id=pk).exists():
            return Response(
                {"error": "Delivery with this output has already arrived."},
                status=status.HTTP_400_BAD_REQUEST
            )

        output = Output.objects.filter(id=pk).first()
        if not output:
            return Response(
                {"error": "Output not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        employee = Employee.objects.filter(id=request.data.get('employee')).first()
        if not employee:
            return Response(
                {"error": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        output = Output.objects.filter(id=pk).first()
        employee = Employee.objects.filter(id=request.data['employee']).first()
        delivery_arrived = DelievaryArrived.objects.create(
            output_receipt=output,
            employee = employee
        )
        del_arr_serializer = DelevaryArrivedSerializer(delivery_arrived, many=False)
        
        user = CustomUser.objects.get(phonenumber=delivery_arrived.employee.phonenumber)
        devices = FCMDevice.objects.filter(user=user.id)
        title = "طلب توصيل جديد"
        body = "لديك طلب جديد لتوصيله"
        devices.send_message(
            message=Message(
                notification=Notification(
                    title=title,
                    body= body
                ),
            ),
        )
        Notifications.objects.create(
            user=user,
            title = title,
            body=body
        )
        return Response(del_arr_serializer.data)

    def get(self, request):
        delivery_arrived = DelievaryArrived.objects.all()
        for delivery in delivery_arrived:
            print(delivery.output_receipt)
        del_arr_serializer = DelevaryArrivedSerializer(delivery_arrived, many=True)
        return Response(del_arr_serializer.data)
    


class GetDelevaryArrivedForEmployee(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        delevary_arrived = DelievaryArrived.objects.filter(id=pk).first()
        serializer = DelevaryArrivedSerializer(delevary_arrived, many=False)
        output = Output.objects.filter(id=delevary_arrived.output_receipt.id).first()
        print(output.id)
        products = Output_Products.objects.filter(output__id= output.id)
        products_serializer = GetProductsOutputsSerializer(products, many=True, context={'request': request})
        receipt_serializer = OutputSerializer(output)
        return Response({'receipt':receipt_serializer.data, 'products':products_serializer.data , 'is_delivered':serializer.data['is_delivered']})




class AcceptDelevaryArrived(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        delevary_arrived = DelievaryArrived.objects.filter(id=pk).first()
        delevary_arrived.is_delivered = request.data['state']
        delevary_arrived.save()
        return Response(status=status.HTTP_200_OK)



########################################## INCOMING ####################################### 

class CreateIncomingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, medium_id):
        incoming_serializer = IncomingSerializer(data=request.data, context={'request': request})
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
            medium = Medium.objects.get(id=medium_id)
            medium.delete()
            return Response(incoming_serializer.data)
        return Response(incoming_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    



class GetIncoming(RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer2

    def get_serializer_context(self):
        return {'show_datetime': True}


class ListIncomings(ListAPIView):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}


class UpdateIncomingReceipt(RetrieveUpdateDestroyAPIView):
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer

class RetUpdDesIncomingProduct(RetrieveUpdateDestroyAPIView):
    queryset = Incoming_Product.objects.all()
    serializer_class = IncomingProductsSerializer2

    def perform_destroy(self, instance):
        product = instance.product
        product.quantity += instance.num_item
        product.save()
        instance.delete()

class CreateIncomingProduct(CreateAPIView):
    queryset = Incoming_Product.objects.all()
    serializer_class = IncomingProductsSerializer2



############################### MANUAL RECEIPT #####################################################
    


class CreateManualReceiptView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, medium_id):
        manual_receipt_serializer = ManualRecieptSerializer(data=request.data, context={'request': request})
        if manual_receipt_serializer.is_valid():
            total_points = 0
            manual_receipt = manual_receipt_serializer.save()
            products = Products_Medium.objects.filter(medium__id=medium_id)
            for product in products:
                update_quantity =Product.objects.get(id=product.product.id)
                update_quantity.quantity -= product.num_item
                update_quantity.save()
                if update_quantity.quantity < update_quantity.limit_less:
                    user = CustomUser.objects.get(id=request.user.id)
                    devices = FCMDevice.objects.filter(user=user.id)
                    title = 'نقص كمية منتج'
                    body = f'يرجى الانتباه وصل الحد الأدنى من كمية المنتج {update_quantity.name}إلى أقل من 10'
                    devices.send_message(
                        message=Message(
                            notification=Notification(
                                title=title,
                                body=body
                            ),
                        ),
                    )
                    Notifications.objects.create(
                        user = user,
                        title = title,
                        body = body
                    ) 
                manual_receipt_products = ManualReceipt_Products.objects.create(
                    product = product.product,
                    manualreceipt = manual_receipt,
                    num_item = product.num_item,
                    price=product.price,
                    total_price = product.total_price_of_item,
                )
                total_points += manual_receipt_products.product_points
            client_points = Points.objects.create(
                client = manual_receipt.client,
                number = total_points
            )
            products.delete()
            medium = Medium.objects.get(id=medium_id)
            medium.delete()
            return Response(manual_receipt_serializer.data)
        return Response(manual_receipt_serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class GetManualReceipt(RetrieveAPIView):
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer2

    def get_serializer_context(self):
        return {'show_datetime': True}



class ListManualReceipt(ListAPIView):
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}


class UpdateManualReceipt(RetrieveUpdateDestroyAPIView):
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer

class RetUpdDesManualReceiptProduct(RetrieveUpdateDestroyAPIView):
    queryset = ManualReceipt_Products.objects.all()
    serializer_class = ManualRecieptProductsSerializer2

    def perform_destroy(self, instance):
        product = instance.product
        product.quantity += instance.num_item
        product.save()
        instance.delete()

class CreateManualProduct(CreateAPIView):
    queryset = ManualReceipt_Products.objects.all()
    serializer_class = ManualRecieptProductsSerializer2


########################## MEDIUM 2 #######################################################################################




class CreateMediumTwo(ListCreateAPIView):
    queryset = MediumTwo.objects.all()
    serializer_class = MediumTwoSerializer
    # permission_classes = [permissions.IsAuthenticated]


class DesMediumTwo(DestroyAPIView):
    queryset = MediumTwo_Products.objects.all()
    serializer_class = MediumTwo_ProductsSerializer
    # permission_classe = [permissions.IsAuthenticated]


class ListMediumTwoProducts(APIView):
    def get(self,request,medium2_id):
        products = MediumTwo_Products.objects.filter(mediumtwo__id=medium2_id)
        serializer = MediumTwo_ProductsSerializer(products,many=True,context={'request':request})
        return Response(serializer.data)


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
        mediumtwo_serializer = MediumTwo_ProductsSerializer(mediumtwo_products, context={'request': request})
        return Response(mediumtwo_serializer.data, status=status.HTTP_201_CREATED)
    

class DeleteMediumTwo(DestroyAPIView):
    queryset = MediumTwo.objects.all()
    serializer_class = MediumTwoSerializer


class MediumTow_Handler(APIView):
    def post(self, request, mediumtwo_id, pk2):
        item = MediumTwo_Products.objects.get(id=mediumtwo_id)
        if pk2 == 'add':
            item.add_item()
            serializer = MediumTwo_ProductsSerializer(item,many=False, context={'request': request})
            return Response(serializer.data)
        else:
            if item.quantity == 1:
                item.delete()
            else:
                item.sub_item()
            serializer = MediumTwo_ProductsSerializer(item,many=False, context={'request': request})
        return Response(serializer.data)
    


class CreateOrderEnvoyView(APIView):
    def post(self, request, mediumtwo_id):
        mediumtwo = MediumTwo_Products.objects.filter(mediumtwo__id = mediumtwo_id)
        order_envoy_ser = OrderEnvoySerializer(data={
            'client':request.data['client'],
            'phonenumber': request.data['phonenumber'],
            'delivery_date':request.data['delivery_date'],
            'address' : request.data['address']
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
    
