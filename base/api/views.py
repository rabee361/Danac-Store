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


class ListCreateSupplier(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer



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



class Medium_Handler(APIView):
    def post(self,request,pk,pk2):
        item = Medium_Products.objects.get(id=pk)
        if pk2 == 'add':
            item.add_item()
            serializer = ProductsMediumSerializer(item,many=False)
            return Response(serializer.data)
        else:
            item.sub_item()
            if item.num_item == 1:
                item.delete()
            serializer = ProductsMediumSerializer(item,many=False)
        return Response(serializer.data)


class GetMediumView(RetrieveAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CreateMedium(CreateAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer


class Add_to_Medium(APIView):
    def post(self,request,pk,pk2):
        medium = Medium.objects.get(id=pk2)
        item = Product.objects.get(id=pk)
        medium_products = Medium_Products.objects.get_or_create(product=item, medium=medium)
        # serializer = Cart_ProductsSerializer(medium_products)
        return Response("تمت اضافة المنتج الى الجدول الوسيط")    



class CreateMediumFromOrderView(APIView):
    def post(self, request, order_id):
        medium = Medium.objects.create()
        order = Order.objects.get(id=order_id)
        order_products = Order_Product.objects.filter(order=order)
        for order_product in order_products:
            medium = Medium_Products.objects.create(medium=medium,product=order_product.product, quantity=order_product.quantity)
        mediums = Medium.objects.all()    
        serializer = MediumSerializer(mediums, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class ReceiptOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, medium_id):
        # manual_reciept = request.data
        client_id = request.data['client']
        client = Client.objects.filter(id=client_id).first()
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        output_serializer = OutputsSerializer(data={
            "employee":employee.id,
            "client": client.id,
            "verify_code": request.data['verify_code'],
            "recive_pyement": request.data['recive_pyement'],
            "phonenumber":request.data['phonenumber'], 
            "discount":request.data['discount'],
            "Reclaimed_products": request.data['Reclaimed_products'],
            "previous_depts": request.data['previous_depts'],
            "remaining_amount":request.data['remaining_amount'],
            
        })
        if output_serializer.is_valid():
            output = output_serializer.save()
            products = Medium_Products.objects.filter(medium__id=medium_id)
            for product in products:
                quantity_product = Product.objects.get(id=product.product.id)
                quantity_product.quantity -= product.num_item
                quantity_product.save()
                output_product = Outputs_Products.objects.create(
                    products = product.product,
                    output = output,
                    quantity = product.num_item,
                    discount = product.discount,
                    total = product.total_price
                )
            products.delete()
            return Response(output_serializer.data)
        return Response(output_serializer.errors)



# class CreateReceiptOrdersView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, **kwargs):
#         # manual_reciept = request.data
#         client_id = request.data['client']
#         client = Client.objects.filter(id=client_id).first()
#         employee = Employee.objects.get(phonenumber=request.user.phonenumber)
#         output_serializer = OutputsSerializer(data={
#             'employee':employee.id,
#             "client": client.id,
#             "verify_code": request.data['verify_code'],
#             "recive_pyement": request.data['recive_pyement'],
#             "phonenumber":request.data['phonenumber'], 
#             "discount":request.data['discount'],
#             "Reclaimed_products": request.data['Reclaimed_products'],
#             "previous_depts": request.data['previous_depts'],
#             'remaining_amount':request.data['remaining_amount'],
            
#         })
#         if output_serializer.is_valid():
#             output = output_serializer.save()
#             products = Medium.objects.all()
#             for product in products:
#                 output_product = Outputs_Products.objects.create(
#                     products = product.products,
#                     output = output,
#                     quantity = product.quantity,
#                     discount = product.discount,
#                     total = product.total
#                 )
#                 product.delete()
#             return Response(output_serializer.data)
#         return Response(output_serializer.errors)



# class ListReceiptOutput(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    # def get(self, request, output_id):
    #     products = Outputs_Products.objects.all()
    #     output_serializer = ProductsOutputsSerializer(products, many=True)
    #     return Response(output_serializer.data)



# --------------------------------------CREATE MEDIUM--------------------------------------
# class CreateMedium(APIView):
#     def post(self, request):
#         medium = Medium.objects.create()
#         return Response(status=status.HTTP_200_OK)

# class CreateMediumView(APIView):
#     def post(self, request, order_id):
#         order = Order.objects.get(id=order_id)
#         medium = Medium.objects.create()
#         order_produdts = Order_Product.objects.filter(order=order)
#         for product in order_produdts:
#             medium_products = Products_Medium.objects.create(
#                 product = product.products,
#                 medium = medium,
#                 num_item=product.quantity,
#                 total_price=product.total_price
#             )
#         return Response(status=status.HTTP_200_OK)
        
# class ReceiptOrdersView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, medium_id):
#         # manual_reciept = request.data
#         client_id = request.data['client']
#         client = Client.objects.filter(id=client_id).first()
#         employee = Employee.objects.get(phonenumber=request.user.phonenumber)
#         output_serializer = OutputsSerializer(data={
#             'employee':employee.id,
#             "client": client.id,
#             "verify_code": request.data['verify_code'],
#             "recive_pyement": request.data['recive_pyement'],
#             "phonenumber":request.data['phonenumber'], 
#             "discount":request.data['discount'],
#             "Reclaimed_products": request.data['Reclaimed_products'],
#             "previous_depts": request.data['previous_depts'],
#             'remaining_amount':request.data['remaining_amount'],
            
#         })
#         if output_serializer.is_valid():
#             output = output_serializer.save()
#             products = Products_Medium.objects.filter(medium__id=medium_id)
#             for product in products:
#                 quantity_product = Product.objects.get(id=product.product.id)
#                 quantity_product.quantity -= product.num_item
#                 quantity_product.save()
#                 output_product = Outputs_Products.objects.create(
#                     products = product.product,
#                     output = output,
#                     quantity = product.num_item,
#                     discount = product.discount,
#                     total = product.total_price
#                 )
#             products.delete()
#             return Response(output_serializer.data)
#         return Response(output_serializer.errors)
    
# class Medium_Handler(APIView):
#     def post(self,request,pk,pk2):
#         item = Products_Medium.objects.get(id=pk)
#         if pk2 == 'add':
#             item.add_item()
#             serializer = ProductsMediumSerializer(item,many=False)
#             return Response(serializer.data)
#         else:
#             item.sub_item()
#             if item.num_item == 1:
#                 item.delete()
#             serializer = ProductsMediumSerializer(item,many=False)
#         return Response(serializer.data)
    
# class GetMediumView(RetrieveAPIView):
#     queryset = Medium.objects.all()
#     serializer_class = MediumSerializer

# class ListMediumView(APIView):
# #     # permission_classes = [permissions.IsAuthenticated]
    
#     def get(self, request, medium_id):
#         mediums = Products_Medium.objects.filter(medium__id=medium_id)
#         mediums_serializer = ProductsMediumSerializer(mediums, many=True)
#         return Response(mediums_serializer.data)




# ------------------------------------------RETURNED GOODS------------------------------------------

class ListCreateRetGoodsSupplier(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        supplier = Supplier.objects.get(id = request.data['supplier'])
        product = Product.objects.get(id=request.data['product'])
        product.quantity -= int(request.data['quantity'])
        product.save()
        return_serializer = ReturnedGoodsSupplierSerializer(data={
            'product':product.id,
            'employee':employee.id,
            'supplier':supplier.id,
            'quantity':request.data['quantity'],
            'total_price':request.data['total_price'],
            'reason':request.data['reason']
        })
        if return_serializer.is_valid():
            return_serializer.save()
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
    def get(self, request):
        products = ReturnedGoodsSupplier.objects.all()
        serializer = ReturnedGoodsSupplierSerializer(products, many=True)
        return Response(serializer.data)


class RetUpdDesReturnGoodSupplier(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    # permission_classes = [permissions.IsAuthenticated]

    
class ListCreateRetGoodsClient(APIView):
    # permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        user = request.user
        employee = Employee.objects.get(phonenumber=user.phonenumber)
        client = Client.objects.get(id = request.data['client'])
        product = Product.objects.get(id=request.data['product'])
        product.quantity += int(request.data['quantity'])
        product.save()
        return_serializer = ReturnedGoodsClientSerializer(data={
            'product':product.id,
            'employee':employee.id,
            'client':client.id,
            'quantity':request.data['quantity'],
            'total_price':request.data['total_price'],
            'reason':request.data['reason']
        })
        if return_serializer.is_valid():
            return_serializer.save()
            return Response(return_serializer.data, status=status.HTTP_201_CREATED)
        return Response(return_serializer.errors)
    

    def get(self, request):
        products = ReturnedGoodsClient.objects.all()
        serializer = ReturnedGoodsClientSerializer(products, many=True)
        return Response(serializer.data)



class RetUpdDesReturnGoodClient(RetrieveUpdateDestroyAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer
    # permission_classes = [permissions.IsAuthenticated]


# ------------------------------------------DAMAGED PRODUCTS------------------------------------------


class ListCreateDamagedProduct(ListCreateAPIView):
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer
    

class RetUpdDesDamagedProduct(RetrieveUpdateDestroyAPIView):
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer
    # permission_classes = [permissions.IsAuthenticated]