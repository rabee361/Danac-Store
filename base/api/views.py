from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView , ListCreateAPIView
from .validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated  ,AllowAny
from rest_framework import status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from base.filters import ProductFilter

class StudentSignupView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        response.data['refresh'] = str(refresh)
        response.data['access'] = str(refresh.access_token)
        return response



class test(ListAPIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        return Response(request.data)



class CurrentUserView(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)



class listProducts(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter



class ListCategory(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GetProduct(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



# class QuantityHandlerView(APIView):
#     def post(self, request, pk, pk2):
#         item = Cart_Products.objects.get(id=pk)
#         if pk2 == 'add':
#             item.add_item()
#         elif pk2 == 'subtract':
#             if item.quantity == 1:
#                 item.sub_item()
#                 item.delete()
#             else:
#                 item.sub_item()
#         else:
#             return Response({"error": "Invalid operation"}, status=status.HTTP_400_BAD_REQUEST)

#         return Response({"success": "Operation performed successfully"}, status=status.HTTP_200_OK)


# def remove_from_cart(request , pk):
#     item = Cart_Products.objects.get(id=pk)
#     item.delete()
#     return redirect(request.META.get('HTTP_REFERER'))


# def add_to_cart(request,pk):
#     item = Product.objects.get(id=pk)
#     cart, created = Cart.objects.get_or_create(customer=request.user)
#     cart_products, created = Cart_Products.objects.get_or_create(products=item, cart=cart)
#     if not created:
#         Cart_Products.objects.filter(products=item, cart=cart).\
#                                 update(quantity=F('quantity') + 1)
#     return redirect(request.META.get('HTTP_REFERER'))


# class ListClients(ListAPIView)
# class getClients
# class createClientView()


# class listSupplier
# class getSupplier
# class createSupplier



# class addToCart
# class listCart
