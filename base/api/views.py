from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
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

class ListCreateOrderView(ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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

# class ListCreateIncomingView(ListCreateAPIView):
#     queryset = Incoming.objects.all()
#     serializer_class = IncomingSerializer

# class CreateIncomingProductsView(APIView):

#     def post(self, request, id):
#         incoming = Incoming.objects.get_or_create(id=id)
#         print(incoming)
#         product_name = request.data['product']
#         product = Product.objects.get(name=product_name)
#         serializer = IncomingProductsSerializer(data={
#             'incoming':incoming.id,
#             'product':product.id,
#             'quantity':request.data['quantity']
#         })
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors)
class ListCreateManualRecieptView(ListCreateAPIView):
    # queryset  = ManualReciept.objects.all()
    # serializer_class = ManualRecieptSerializer
    def post(self, request):
        manualreciept = request.data
        serializer = ManualRecieptSerializer(data=manualreciept)
        print
        if serializer.is_valid():
            manual_reciept = serializer.save()
            manual_products = manualreciept.data['products']
            for manual_product in manual_products:
                manual_product['manualreciept'] = manual_reciept.id
                manualrecieptser = ManualRecieptProductsSerializer(data=manual_product)
                if manualrecieptser.is_valid():
                    manualrecieptser.save()
                    return Response(serializer.data)
                return Response(manualrecieptser.errors)
            return Response(serializer.errors)