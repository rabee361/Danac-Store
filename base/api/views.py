from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, DestroyAPIView ,RetrieveAPIView,UpdateAPIView ,RetrieveUpdateDestroyAPIView, CreateAPIView, GenericAPIView , ListCreateAPIView , RetrieveUpdateAPIView , RetrieveDestroyAPIView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from base.filters import *
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
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




class RefreshFirebaseToken(GenericAPIView):
    # permission_classes = [IsAuthenticated]
    def post(self,request):
        token = request.data['firebase-token']
        user_id = request.data['user_id']
        try:
            user = CustomUser.objects.get(id=user_id)
            device = FCMDevice.objects.get(user=user)
            device.registration_id = token
            device.save()
        except:
            raise CustomUser.DoesNotExist

        return Response({
            "msg" : "firebase token changed successfully"
        })






class UserLoginApiView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = CustomUser.objects.get(phonenumber = request.data['username'])
        token = RefreshToken.for_user(user)

        chat = Chat.objects.filter(user=user).first()


        data = serializer.data
        if chat:
            data['chat_id'] = chat.id
        data['image'] = request.build_absolute_uri(user.image.url)
        data['id'] = user.id
        data['longitude'] = user.location.x
        data['laritude'] = user.location.y
        data['address'] = user.address
        data['tokens'] = {'refresh':str(token), 'access':str(token.access_token)}
        return Response(data, status=status.HTTP_200_OK)
    

class UpdateImageUserView(APIView):
    def put(self, requset, user_pk):
        user = CustomUser.objects.get(id=user_pk)
        serializer = UpdateUserSerializer(user, data=requset.data, many=False, context={'request':requset})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'success':"The Profile Image has been changed successfully.",
                 'image' : serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)




class GetNotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notification = UserNotification.objects.filter(user__id=user.id)
        serializer = SerializerNotification(notification, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class ResetPasswordView(UpdateAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny,]

    def put(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        if user.is_verified:
            data = request.data
            serializer = self.get_serializer(data=data, context={'user_id':user_id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            messages = {
                'message':'تم تغيير كلمة المرور بنجاح'
            }
            return Response(messages, status=status.HTTP_200_OK)
        
        else:
            return Response({'error':'ليس لديك صلاحية لتغيير كلمة المرور'})





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



# class GetPhonenumberView(APIView):
#     def post(self, request):
#         email = request.data['email']
#         try: 
#             user = get_object_or_404(CustomUser, email=email)
#             existing_code = CodeVerification.objects.filter(user=user).first()
#             if existing_code:
#                 existing_code.delete()

#             code_verivecation = random.randint(1000,9999)
#             # email_body = 'Hi '+user.username+' Use the code below to verify your email \n'+ str(code_verivecation)
#             data= {'to_email':user.email, 'email_subject':'Verify your email','username':user.username, 'code': str(code_verivecation)}
#             Utlil.send_email(data)
#             serializer = CodeVerivecationSerializer(data ={
#                 'user':user.id,
#                 'code':code_verivecation,
#                 'is_verified':False,
#                 'expires_at' : timezone.now() + timedelta(minutes=10)
#             })
#             serializer.is_valid(raise_exception=True)
#             serializer.save()
#             return Response({'message':'تم ارسال رمز التحقق',
#                              'user_id' : user.id})
#         except:
#             raise serializers.ValidationError({'error':'pleace enter valid email'})



class VerefyPhonenumberView(APIView):
    def post(self, request):
        phonenumber = request.data['phonenumber']
        user_id = request.data['user_id']
        user = CustomUser.objects.filter(phonenumber=phonenumber).first()
        if user.id != int(user_id):
            return Response({'error':"user not found"})
        user.is_verified = True
        user.save()
        return Response({'user_id':user.id}, status=status.HTTP_200_OK)


#### delete
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



class States(ListAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer



class GetState(RetrieveAPIView):
    queryset = State.objects.all()
    serializer_class = StateSerializer


######################################### CART & PRODUCTS ##########################################################################



class ListAds(ListAPIView):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer


class GetTotalCategories(APIView):
    def get(self,request):
        total_categories = Category.objects.count()
        return Response({
            "total_categories":total_categories
        })
    

class GetTotalProductTypes(APIView):
    def get(self,request):
        total_product_types = ProductType.objects.count()
        return Response({
            "total_product_types":total_product_types
        })



class ListCreateProductType(ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductTypeFilter

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




class RetUpdDesProductType(RetrieveUpdateDestroyAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer




class ListCreateCategory(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CategoryFilter

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


class listCreateProducts(ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
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





#################################################### CART HNADLING #####################################################################

class Cart_Items(APIView):
    permission_classes = [IsAuthenticated,Is_Client]
    def get(self,request,pk):
        products = Cart_Products.objects.filter(cart=pk)
        serializer = Cart_ProductsSerializer(products,many=True, context={'request': request})
        return Response(serializer.data)


class Client_Details(APIView):
    def get(self,request,pk):
        user = CustomUser.objects.get(id=pk)
        client = Client.objects.get(phonenumber=user.phonenumber)
        serializer = Client_DetailsSerializer(client,many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)



class Cart_Items_Details(APIView):
    # permission_classes = [IsAuthenticated,Is_Client]
    def get(self,request,pk):
        products = Cart_Products.objects.filter(cart=pk)
        serializer = Cart_Product_DetailsSerialzier(products,many=True, context={'request': request})
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
        quantity = request.data.get('quantity')
        cart_product,created = Cart_Products.objects.get_or_create(products=item,cart=cart)

        if quantity :
            cart_product.quantity = quantity
            cart_product.save()

        serializer = Cart_ProductsSerializer2(cart_product,many=False)
        return Response(serializer.data,status=status.HTTP_201_CREATED)


        # if not created:
        #     # Cart_Products.objects.filter(products=item, cart=cart).\
        #     #                         update(quantity=F('quantity') + 1)
        #     product = Cart_Products.objects.get(products=item, cart=cart)
        #     serializer = Cart_ProductsSerializer2(product,many=False)
        #     return Response(serializer.data,status=status.HTTP_201_CREATED)       


                        # Cart_Products.objects.filter(products=item, cart=cart).\
                        #             update(quantity=F('quantity')+request.data['quantity'])



class Delete_From_Cart(DestroyAPIView):
    permission_classes = [IsAuthenticated,Is_Client]
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_Products


###################################### ORDER HANDLING ############################################################################################


class CreateOrderView(APIView):
    # permission_classes = [IsAuthenticated,Is_Client]

    def post(self, request, cart_id):

        ### check if the cart is empty
        cart = get_object_or_404(Cart, id=cart_id)
        if cart.get_items_num == 0: 
            return Response({"error": "السلة فارغة لا يمكن إنشاء طلب"}, status=status.HTTP_400_BAD_REQUEST)
        
        delivery_date = request.data.get('delivery_date')
        if not delivery_date:
            return Response({"error": "Delivery date is required"}, status=status.HTTP_400_BAD_REQUEST)
        order = cart.create_order(delivery_date)

        ### sending a notification
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
        UserNotification.objects.create(user=user,body=body,title=title)

        order.save()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
     


class ListOrders(ListAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter
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
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SalesEmployeeFilter
    ordering_fields = ['name', 'truck_num']

    def get(self, request):
        sales_employees = Employee.objects.filter(Q(truck_num__gt=0) & Q(truck_num__isnull=False))
        filtered_sales_employees = self.filterset_class(request.GET, queryset=sales_employees)
        serializer = SalesEmployeeSerializer(filtered_sales_employees.qs, many=True)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeFilter
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesEmployee(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class RetUpdDesClient(RetrieveAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


    
class ListCreateClient(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClientFilter
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class ListCreateSupplier(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = SupplierFilter
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class RetUpdDesClient(RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


########################################### HR ######################################################################


class RetUpdDesEmployee(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class ListCreatOverTime(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = OverTimeFilter
    queryset = OverTime.objects.all()
    serializer_class = OverTimeSerializer

class RetUpdDesOverTime(RetrieveUpdateDestroyAPIView):
    queryset = OverTime.objects.all()
    serializer_class = OverTimeSerializer

class ListCreateAbsence(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = AbsenceFilter
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class RetUpdDesAbsence(RetrieveUpdateDestroyAPIView):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer

class ListCreateBonus(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = BonusFilter
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer

class RetUpdDesBonus(RetrieveUpdateDestroyAPIView):
    queryset = Bonus.objects.all()
    serializer_class = BonusSerializer

class ListCreateDicount(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = DiscountFilter
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class RetUpdDesDicount(RetrieveUpdateDestroyAPIView):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

class ListCreateAdvance(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = Advance_On_salaryFilter
    queryset = Advance_On_salary.objects.all()
    serializer_class = Advance_on_SalarySerializer

class RetUpdDesAdvance(RetrieveUpdateDestroyAPIView):
    queryset = Advance_On_salary.objects.all()
    serializer_class = Advance_on_SalarySerializer

class ListCreateExtraExpense(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = Extra_ExpenseFilter
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



class GetRegistryOperations(APIView):
    def post(self,request):
        operation = request.data.get('operation', None)
        receipt_num = request.data.get('receipt_num', None)

        operations_dict = {
            'مدفوعات': (Payment, PaymentSerializer),
            'مقبوضات': (Recieved_Payment, RecievedPaymentSerializer),
            'مصاريف': (Expense, ExpenseSerializer),
            'ديون عميل': (Debt_Client, Client_DebtSerializer),
            'ديون مورد': (Debt_Supplier, Supplier_DebtSerializer),
        }
        if operation in operations_dict:
            model, serializer_class = operations_dict[operation]
            instance = model.objects.filter(receipt_num=receipt_num).first()
            instance.added_to_registry = True
            instance.save()
            serializer = serializer_class(instance, many=False)
            return Response(serializer.data)
        else:
            return Response({
                "msg": "لا يوجد عملية بهذا الاسم"
            })



class ListRegistries(ListAPIView):
    serializer_class = RegistrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = Employee.objects.get(phonenumber=self.request.user.phonenumber)
        try:
            employee = Employee.objects.get(phonenumber=self.request.user.phonenumber)
            queryset = Registry.objects.filter(employee=employee)
            return queryset
        except ObjectDoesNotExist:
            return Registry.objects.none()



class ListCreateClientDebts(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = DebtClientFilter
    queryset = Debt_Client.objects.all()
    serializer_class = Client_DebtSerializer


class ListCreateSupplierDebts(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = DebtSupplierFilter
    queryset = Debt_Supplier.objects.all()
    serializer_class = Supplier_DebtSerializer


class RetUpdDesSupplierDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt_Supplier.objects.all()
    serializer_class = Supplier_DebtSerializer


class RetUpdDesClientDebt(RetrieveUpdateDestroyAPIView):
    queryset = Debt_Client.objects.all()
    serializer_class = Client_DebtSerializer


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
    filter_backends = [DjangoFilterBackend]
    filterset_class = DepositeFilter
    queryset = Deposite.objects.all()
    serializer_class = DepositeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = Employee.objects.get(phonenumber=self.request.user.phonenumber)
        employee_registry = Registry.objects.get(employee=employee)
        queryset = Deposite.objects.filter(registry=employee_registry)
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class RetUpdDesDeposite(RetrieveUpdateDestroyAPIView):
    queryset = Deposite.objects.all()
    serializer_class = DepositeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    

class ListCreateWithDraw(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = WithdrawFilter
    queryset = WithDraw.objects.all()
    serializer_class = WithDrawSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        employee = Employee.objects.get(phonenumber=self.request.user.phonenumber)
        employee_registry = Registry.objects.get(employee=employee)
        queryset = WithDraw.objects.filter(registry=employee_registry)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    


class RetUpdDesWithDraw(RetrieveUpdateDestroyAPIView):
    queryset = WithDraw.objects.all()
    serializer_class = WithDrawSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    


class ListCreatePayment(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class RetUpdDesPayment(RetrieveUpdateDestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class ListCreateRecievedPayment(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = Recieved_PaymentFilter
    queryset = Recieved_Payment.objects.all()
    serializer_class = RecievedPaymentSerializer


class RetUpdDesRecievedPaymnt(RetrieveUpdateDestroyAPIView):
    queryset = Recieved_Payment.objects.all()
    serializer_class = RecievedPaymentSerializer


class ListCreateExpense(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ExpenseFilter
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class RetUpdDesExpense(RetrieveUpdateDestroyAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


#####################################################################################################################


# ------------------------------------------DAMAGED & RETURNED PRODUCTS------------------------------------------


class ListReturnedSupplierPackages(ListCreateAPIView):
    queryset = ReturnedSupplierPackage.objects.all()
    serializer_class = ReturnedSupplierPackageSerializer
 


class RetReturnedSupplierPackages(RetrieveAPIView):
    queryset = ReturnedSupplierPackage.objects.all()
    serializer_class = ReturnedSupplierPackageSerializer

    # manual_receipt_serializer = ManualRecieptSerializer(data=request.data, context={'request': request})


class ListCreateRetGoodsSupplier(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReturnedGoodsSupplierFilter
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self,serializer):
        user = self.request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        serializer.save(employee=employee)


class RetUpdDesReturnGoodSupplier(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    # permission_classes = [permissions.IsAuthenticated]    




class ListReturnedClientPackages(ListCreateAPIView):
    queryset = ReturnedClientPackage.objects.all()
    serializer_class = ReturnedClientPackageSerializer


class RetReturnedClientPackages(RetrieveAPIView):
    queryset = ReturnedClientPackage.objects.all()
    serializer_class = ReturnedClientPackageSerializer


class ListCreateRetGoodsClient(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ReturnedGoodsClientFilter
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer
    permission_classes = [permissions.IsAuthenticated]    

    def perform_create(self,serializer):
        user = self.request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        serializer.save(employee=employee)   



class RetUpdDesReturnGoodClient(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer
    # permission_classes = [permissions.IsAuthenticated]



class ListDamagedPackages(ListCreateAPIView):
    queryset = DamagedPackage.objects.all()
    serializer_class = DamagedPackageSerializer



class RetDamagedPackages(RetrieveUpdateDestroyAPIView):
    queryset = DamagedPackage.objects.all()
    serializer_class = DamagedPackageSerializer



class ListCreateDamagedProduct(ListCreateAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = DamagedProductFilter
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer
    permission_classes = [permissions.IsAuthenticated]  

    def perform_create(self,serializer):
        user = self.request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        serializer.save(employee=employee)   




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

    


class Add_product_to_Medium(APIView):
    def post(self,request):
        product_id = self.request.data['product']
        medium_id = self.request.data['medium']
        product = Product.objects.get(id=product_id)
        medium = Medium.objects.get(id=medium_id)
        num_item = self.request.data['num_item']
        sale_price = self.request.data['sale_price']
        medium_products, created = Products_Medium.objects.get_or_create(product=product, medium=medium)
        if created:
            medium_products.price += float(sale_price)
            medium_products.num_item += int(num_item)
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


class FreezeOutputReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = Output.objects.get(id=receipt_id)
            reason = request.data.get('reason')
            if not reason:
                return Response({
                    "msg":"provide the reason for freezing"
                })
            receipt.freeze = True
            receipt.save()
            freeze_receipt,created = FrozenOutputReceipt.objects.get_or_create(receipt=receipt)
            freeze_receipt.reason = reason
            freeze_receipt.save()
            return Response({
                "msg":"receipt freezed"
            })
        except Output.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })
        


class UnFreezeOutputReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = Output.objects.get(id=receipt_id)
            receipt.freeze = False
            receipt.adjustment_applied = False
            receipt.save()
            freeze_receipt = FrozenOutputReceipt.objects.get(receipt=receipt)
            freeze_receipt.save()
            freeze_receipt.delete()
            return Response({
                "msg":"receipt unfreezed"
            })
        except Output.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })




class GetOutput(RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2

    def get_serializer_context(self):
        return {'show_datetime': True}


class ListOutputs(ListAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = OutputFilter
    queryset = Output.objects.all()
    serializer_class = OutputSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}


class ListFrozenOutputReceipts(ListAPIView):
    queryset = FrozenOutputReceipt.objects.all()
    serializer_class = FrozenOutputReceiptSerializer



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
                    UserNotification.objects.create(
                        user = user,
                        title = title,
                        body = body
                    )
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
        UserNotification.objects.create(
            user=user,
            title = title,
            body=body
        )
        return Response(del_arr_serializer.data)

    def get(self, request):
        queryset = DelievaryArrived.objects.all()
        filterset = DelivaryFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            delivery_arrived = filterset.qs
        else:
            return Response(filterset.errors, status=status.HTTP_400_BAD_REQUEST)
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = IncomingFilter
    queryset = Incoming.objects.all()
    serializer_class = IncomingSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}



class ListFrozenIncomingReceipts(ListAPIView):
    queryset = FrozenIncomingReceipt.objects.all()
    serializer_class = FrozenIncomingReceiptSerializer



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



class FreezeIncomingReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = Incoming.objects.get(id=receipt_id)
            reason = request.data.get('reason')
            if not reason:
                return Response({
                    "msg":"provide the reason for freezing"
                })
            receipt.freeze = True
            receipt.save()
            freeze_receipt,created = FrozenIncomingReceipt.objects.get_or_create(receipt=receipt)
            freeze_receipt.reason = reason
            freeze_receipt.save()
            return Response({
                "msg":"receipt freezed"
            })
        except Incoming.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })

        
class UnFreezeIncomingReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = Incoming.objects.get(id=receipt_id)
            receipt.freeze = False
            receipt.adjustment_applied = False
            receipt.save()
            freeze_receipt = FrozenIncomingReceipt.objects.get(receipt=receipt)
            freeze_receipt.save()
            freeze_receipt.delete()
            return Response({
                "msg":"receipt unfreezed"
            })
        except Incoming.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })

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
                    UserNotification.objects.create(
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
    filter_backends = [DjangoFilterBackend]
    filterset_class = ManualFilter
    queryset = ManualReceipt.objects.all()
    serializer_class = ManualRecieptSerializer2

    def get_serializer_context(self):
        return {'show_datetime': False}


class ListFrozenManualReceipts(ListAPIView):
    queryset = FrozenManualReceipt.objects.all()
    serializer_class = FrozenManualReceiptSerializer


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



class FreezeManualReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = ManualReceipt.objects.get(id=receipt_id)
            reason = request.data.get('reason')
            if not reason:
                return Response({
                    "msg":"provide the reason for freezing"
                })
            receipt.freeze = True
            receipt.save()
            freeze_receipt,created = FrozenManualReceipt.objects.get_or_create(receipt=receipt)
            freeze_receipt.reason = reason
            freeze_receipt.save()
            return Response({
                "msg":"receipt freezed"
            })
        except ManualReceipt.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })
        

class UnFreezeManualReceipt(APIView):
    def post(self,request,receipt_id):
        try:
            receipt = ManualReceipt.objects.get(id=receipt_id)
            receipt.freeze = False
            receipt.adjustment_applied = False
            receipt.save()
            freeze_receipt = FrozenManualReceipt.objects.get(receipt=receipt)
            freeze_receipt.save()
            freeze_receipt.delete()
            return Response({
                "msg":"receipt unfreezed"
            })
        except ManualReceipt.DoesNotExist:
            return Response({
                "msg":"receipt doesn't exist"
            })
        
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
    



########################### chat ##########################
    

class SendMessage(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self,request,chat_id,user_id):
        user = CustomUser.objects.get(id=user_id)
        chat = Chat.objects.get(id=chat_id)
        message = self.request.data['message']

        try:
            Employee.objects.get(phonenumber=user.phonenumber)
            msg = ChatMessage.objects.create(sender=user,content=message,chat=chat,employee=True)
        except Employee.DoesNotExist:
            msg = ChatMessage.objects.create(sender=user,content=message,chat=chat,employee=False)
        serializer = MessageSerializer(msg,many=False)

        return Response(serializer.data)



class ChatMessages(APIView):
    def get(self,request,chat_id):
        chat = Chat.objects.get(id=chat_id)
        messages = ChatMessage.objects.filter(chat=chat)
        serializer = MessageSerializer(messages,many=True)
        return Response(serializer.data)
    

class Chats(APIView):
    def get(self,request):
        chats = Chat.objects.all()
        serializer = ChatSerializer(chats,many=True, context={'request': request})
        return Response(serializer.data)
    

class GetChat(RetrieveAPIView):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer