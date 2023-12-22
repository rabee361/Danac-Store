from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView
from .validation import custom_validation
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from base.filter import ProductFilter, ProductFilterName
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import random
from rest_framework import filters
from .permissions import IsManager, IsDriver



class SingupView(GenericAPIView):

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
    
class UpdateImageUserView(APIView):

    permission_classes=[permissions.IsAuthenticated]

    def put(self, requset, user_pk):

        user_pk = requset.user.id
        user = CustomUser.objects.get(id=user_pk)
        serializer = UpdateUserSerializer(user, data=requset.data, many=False, context={'request':requset})
        if serializer.is_valid():
            serializer.save()
            return Response(

                {'success':"The changed image Profile has been successfully."},
                status=status.HTTP_200_OK
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)

class ListInformationUserView(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class= CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    
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

class VerefyCodeView(APIView):
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

class GetUdpDesProductView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class UserListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class CartProducts(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_ProductsSerializer

    def get_queryset(self):
        client = Client.objects.get(id=1)
        return Cart_Products.objects.filter(cart__customer=client)


class ListPointsView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated,]

    def get(self, request):
        user = request.user
        clinet = Client.objects.get(phomnenumber=user.phonenumber)
        points = clinet.point_set.all()
        serializer = PointSerializer(points, many=True)
        response = serializer.data
        return Response(response)
        



class CreateCartProductsView(ListCreatCategoryView):
    pass


class ListCreateSupplierView(ListCreateAPIView):
    queryset = Supplier.objects.all()
    serializer_class= SupplierSerializer
    # permission_classes = [permissions.IsAuthenticated]


class GetSupplier(RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.all()
    serializer_class= SupplierSerializer


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

# class ListCreateOrderView(ListCreateAPIView):
#     queryset = Order.objects.all()
#     serializer_class = OrderSerializer

class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        client = Client.objects.get(phomnenumber=user.phonenumber)
        cart = Cart.objects.get(customer=client)
        cart_products = Cart_Products.objects.filter(cart=cart)
        order = Order.objects.create(clinet=client, delivery_date=request.data['delivery_date'])
        total = 0.0
        for products_cart in cart_products:     
            order_Products = Order_Product.objects.create(
                products= products_cart.products,
                order = order,
                quantity = products_cart.quantity,
                total_price = products_cart.products.sale_price * products_cart.quantity
            )
            
            order.products_num += products_cart.quantity
            order.total += products_cart.products.sale_price * products_cart.quantity
            order.save()
            products_cart.delete()
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)

        

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

class ListCreateAdvanceView(ListCreateAPIView):
    queryset = Advance.objects.all()
    serializer_class = AdvanceSerializer

class RetUpdDesAdvanceView(RetrieveUpdateDestroyAPIView):
    queryset = Advance.objects.all()
    serializer_class = AdvanceSerializer

class ListCreateExpenceView(ListCreateAPIView):
    queryset = ExtraExpense.objects.all()
    serializer_class = ExpenseSerializer

class RetUpdDesExpenceView(RetrieveUpdateDestroyAPIView):
    queryset = ExtraExpense.objects.all()
    serializer_class = ExpenseSerializer


class SearchView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilterName


class Add_To_Medium(APIView):
    

    def post(self, request, medium_id, product_id):
        prodcut = Product.objects.get(id=product_id)
        medium = Medium.objects.get(id=medium_id)
        medium_products, created = Products_Medium.objects.get_or_create(product=prodcut, medium=medium)
        if created:
            medium_products.add_num_item()
            medium_products.total_price = medium_products.total_price_of_item
            medium_products.save()

        pro_med_serializer = ProductsMediumSerializer(medium_products)
        return Response(pro_med_serializer.data, status=status.HTTP_200_OK)

class CreateIncomingView(APIView):

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
    


# Add Or Get Products From Cart
class ListCreateCartProduct(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        client = Client.objects.filter(phomnenumber=user.phonenumber).first()
        cart = Cart.objects.filter(customer=client).first()
        product = Product.objects.get(id=request.data['id'])
        serializer = Cart_ProductsSerializer(data = {
            'products':product.id,
            'cart':cart.id,
            'quantity':request.data['quantity']
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


    def get(self, request):
        user = request.user
        client = Client.objects.get(phomnenumber = user.phonenumber)
        cart = Cart.objects.get(customer=client)
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)
    
# Update Or Delete Products Form Cart
class DesUpdCartProducts(RetrieveUpdateDestroyAPIView):
    queryset = Cart_Products.objects.all()
    serializer_class = Cart_ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]

class ListReceiptOutput(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, output_id):
        # output = Outputs.objects.get(id=output_id)
        products = Outputs.objects.get(id=output_id)
        output_serializer = OutputsSerializer(products)
        return Response(output_serializer.data)

# --------------------------------------CREATE MEDIUM--------------------------------------
class CreateMedium(APIView):
    # permission_classes = [permissions.IsAuthenticated, IsManager]

    def post(self, request):
        medium = Medium.objects.create()

        return Response(status=status.HTTP_200_OK)
    

class RetDesMedium(RetrieveDestroyAPIView):
    queryset = Medium.objects.all()
    serializer_class = MediumSerializer


class CreateMediumForOrderView(APIView):
    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)
        medium = Medium.objects.create()
        order_produdts = Order_Product.objects.filter(order=order)
        for product in order_produdts:
            medium_products = Products_Medium.objects.create(
                product = product.products,
                medium = medium,
                num_item=product.quantity,
                total_price=product.total_price
            )
        return Response(status=status.HTTP_200_OK)
        
class ReceiptOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, medium_id):
        # manual_reciept = request.data
        client_id = request.data['client']
        client = Client.objects.filter(id=client_id).first()
        employee = Employee.objects.get(phonenumber=request.user.phonenumber)
        output_serializer = OutputsSerializer(data={
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
    

class ListCreateDeliveryArrived(APIView):
    
    def post(self, request, pk):
        output = Outputs.objects.filter(id=pk).first()
        employee = Employee.objects.filter(id=request.data['employee']).first()
        delivery_arrived = DelevaryArrived.objects.create(
            output_receipt=output,
            employee = employee
        )
        del_arr_serializer = DelevaryArrivedSerializer(delivery_arrived, many=False)
        return Response(del_arr_serializer.data)
    

    def get(self, request):
        delivery_arrived = DelevaryArrived.objects.all()
        for delivery in delivery_arrived:
            print(delivery.output_receipt)
        del_arr_serializer = DelevaryArrivedSerializer(delivery_arrived, many=True)
        return Response(del_arr_serializer.data)
    

class Medium_Handler(APIView):
    def post(self, request, pk, pk2):
        item = Products_Medium.objects.get(id=pk)
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
    
class DeleteProductsMediumView(RetrieveDestroyAPIView):
    queryset = Products_Medium.objects.all()
    serializer_class = ProductsMediumSerializer

class UpdateProductsMedium(RetrieveUpdateAPIView):
    queryset = Products_Medium.objects.all()
    serializer_class = UpdateProductMediumSerializer

class ListMediumView(APIView):
#     # permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, medium_id):
        mediums = Products_Medium.objects.filter(medium__id=medium_id)
        mediums_serializer = ProductsMediumSerializer(mediums, many=True)
        return Response(mediums_serializer.data)

# ------------------------------------------RETURNED GOODS------------------------------------------

class ListCreateRetGoodsSupplier(APIView):
    permission_classes = [permissions.IsAuthenticated]

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

class RetDesReturnGoodSupplier(RetrieveDestroyAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = ReturnedGoodsSupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


class UpdateReturnGoodSupplier(RetrieveUpdateAPIView):
    queryset = ReturnedGoodsSupplier.objects.all()
    serializer_class = UpdateReturnGoodSupplierSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListCreateRetGoodsClient(APIView):
    permission_classes = [permissions.IsAuthenticated]

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



class RetDesReturnGoodClient(RetrieveDestroyAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = ReturnedGoodsClientSerializer
    permission_classes = [permissions.IsAuthenticated]

class UpdateReturnGoodClient(RetrieveUpdateAPIView):
    queryset = ReturnedGoodsClient.objects.all()
    serializer_class = UpdateReturnedGoodsClientSerializer
    permission_classes = [permissions.IsAuthenticated]

# ------------------------------------------DAMAGED PRODUCTS------------------------------------------


class CreateDamagedProduct(APIView):
    def post(self, request):
        product = Product.objects.get(id=request.data['product'])
        product.quantity -= int(request.data['quantity'])
        product.save()
        damaged_product = DamagedProduct.objects.create(
            product=product,
            total_price = request.data['total_price'],
            quantity = request.data['quantity']
        )
        serializer = DamagedProductSerializer(damaged_product, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def get(self, request):
        products = DamagedProduct.objects.all()
        serializer = DamagedProductSerializer(products, many=True)
        return Response(serializer.data)
    
class RetUpdDesDamagedProduct(RetrieveUpdateDestroyAPIView):
    queryset = DamagedProduct.objects.all()
    serializer_class = DamagedProductSerializer
    # permission_classes = [permissions.IsAuthenticated]


# -------------------------------------MANUAL RECEIPT-------------------------------------
    
class CreateManualReceiptView(APIView):

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
    
# class GetManualReceiptView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, receipt_id):
#         man
    
from .send_sms import send_sms
# def send(request):
#     sms_body = "Thank you for registering!"
#     send_sms('+963957322954', sms_body)
class SendSms(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        body = "Thank you for registering"
        # to = "+213660030002"
        user = request.user
        # client = Client.objects.get(phomnenumber=user.phonenumber)
        # client_serializer = ClientSerializer(client, many=False)
        # serializer = client_serializer.data
        # print(serializer['phomnenumber'])
        serializer ={
            'phomnenumber':213660020003
        }
        print(type(serializer['phomnenumber']))
        send_sms(serializer['phomnenumber'], body)

        return Response(status=status.HTTP_200_OK)