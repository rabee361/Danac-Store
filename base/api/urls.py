from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


from django.urls import path
from .views import *
urlpatterns = [
    path('sign-up/' , SignupView.as_view()),
    path('auth/reset-password/' , ResetPasswordView.as_view(), name='reset-password'),
    path('sign-in/', UserLoginApiView.as_view(), name='sign-in'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('settings/<str:pk>/', ListInformationUserView.as_view(), name='settings'),
    path('settings/update-image/<int:user_pk>/', UpdateImageUserView.as_view(), name='update-image'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('get-number/', GetPhonenumberView.as_view(), name='get-number'),
    path('verefy-code/', VerefyCodeView.as_view(), name='verefy-code'),
    path('categorys/', ListCreatCategoryView.as_view(), name='catogorys'),
    path('products/', ListCreateProductView().as_view(), name='products'),
    path('get-product/<str:pk>/', GetProductView.as_view()),
    path('suppliers/', ListCreateSupplierView.as_view(), name='suppliers'),
    path('get-supplier/<str:pk>/' , GetSupplier.as_view() , name="get-supplier"),
    path('orders/', ListCreateOrderView().as_view(), name='orders'),
    path('points/', ListPointsView.as_view(), name='points'),
    path('orders/user/', ListOrdersUserView.as_view(), name='orders-user')
    # path('product/category/', UserListView.as_view()),
]
