from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView ,RetrieveUpdateDestroyAPIView, CreateAPIView, GenericAPIView , ListCreateAPIView , RetrieveUpdateAPIView , RetrieveDestroyAPIView
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


class SpecialProducts(APIView):
    def get(self,request):
        products = Product.objects.all().order_by('?')
        serializer = Product2Serializer(products,many=True)
        return Response(serializer.data)



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

############################ CART HNADLING ######################
        
class CartProductsView(ListCreateAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Cart_Products.objects.select_related('products','cart').all()
    serializer_class = Cart_ProductsSerializer

    def get_queryset(self):
        client = Client.objects.get(id=1)
        return Cart_Products.objects.filter(cart__customer=client)
    

class CreateCartView(ListCreateAPIView):
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
            if item.quantity == 0:
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
        



class ListCreateSupplier(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class RetUpdDesClient(RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class RetUpdDesCategory(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

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
    serializer_class = RegistrySerialzier

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


#####################################################################################################################


# ------------------------------------------DAMAGED & RETURNED PRODUCTS------------------------------------------


class ListCreateRetGoodsSupplier(ListCreateAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer

class RetUpdDesReturnGoodSupplier(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    # permission_classes = [permissions.IsAuthenticated]    

class ListCreateRetGoodsClient(ListCreateAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer

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
                item.sub_item()
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
        

class ListReceiptOutput(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, output_id):
        products = Output_Products.objects.filter(output__id=output_id)
        output_serializer = ProductsOutputSerializer(products, many=True)
        return Response(output_serializer.data)


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
        return Response(del_arr_serializer.data)
    




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
    




class CreateIncomingView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, medium_id):
        user = request.user
        supplier = Supplier.objects.get(id=request.data['supplier'])
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        incoming_serializer = IncomingSerializer(data={
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
    


