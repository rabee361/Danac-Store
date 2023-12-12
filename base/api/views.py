from rest_framework.response import Response
from base.models import *
from .serializers import *
from rest_framework.generics import ListAPIView, RetrieveAPIView , CreateAPIView, GenericAPIView
from api.validation import custom_validation
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken


class StudentSignupView(GenericAPIView):

    """
    An endpoint for the client to create a new Student.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentSignupSerializer

    def post(self, request, *args, **kwargs):
        clean_data = custom_validation(request.data)
        serializer = self.get_serializer(data=clean_data)   
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = CustomUser.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user)
        # current_site = get_current_site(request).domain
        # relativelink = reverse('email-verify')
        # absurl = 'http://'+current_site+relativelink+'?token='+str(token.access_token)
        # rand_num = random.randint(1,10000)
        # email_body = 'Hi '+user.username+' Use the link below to verify your email \n'+ absurl
        # data = {'email_body':email_body, 'to_email':user.email, 'ema(il_subject':'Verify your email'}
        # Utlil.send_eamil(data)
        data_user = serializer.data
        data_user['tokens'] = {"refresh" : str(token), "access":str(token.access_token)}
        return Response(
            {
                "user": data_user,
                "message":"account created successfully"
            })





# class ListClients(ListAPIView)
# class getClients
# class createClientView()


# class listSupplier
# class getSupplier
# class createSupplier


# class createProduct
# class getProduct
# class listProduct


# class addToCart
# class listCart
