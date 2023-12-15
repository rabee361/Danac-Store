from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('auth/sign-up/' , SignUpView.as_view()),#####
    path('auth/log-in/', UserLoginApiView.as_view(), name='sign-in'),#####
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),#####
    path('auth/reset-password/' , ResetPasswordView.as_view(), name='reset-password'),####
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('test/' , test.as_view()),
    path('user/' , CurrentUserView.as_view()),
    path('products/' , listCreateProducts.as_view() , name="products"),######
    path('categories/' , ListCreateCategory.as_view() , name="categories"),##### post/get
    path('product/<str:pk>' , GetProduct.as_view() , name="product"),#####
    path('user_items/' , CartProducts.as_view() , name="user_products"),
    path('get-number/', GetPhonenumberView.as_view(), name='get-number'),
    path('suppliers/' , ListCreateSupplier.as_view() , name="suppliers"), ##### post/get
    path('get-supplier/<str:pk>' , GetSupplier.as_view() , name="get-supplier"),##### post/get
    path('orders/' , ListCreateOrder.as_view() ,name="orders"),####
    path('create/' , CreateOrder.as_view() ),
    path('incomings/' , ListCreateIncomings.as_view() , name="incomings"),
    path('incoming_product/' , CreateIncomingProducts.as_view() , name="")
    # path('employees/', ListCreatEmployeeView.as_view(), name='employee'),
    # path('employees/<str:pk>/', RetUpdDesEmployeeAPIView.as_view(), name='get-employee'),
    # path('overtimes/', ListCreatOverTimeView.as_view(), name='overtimes'),
    # path('overtimes/<str:pk>/', RetUpdDesOverTimeView.as_view(), name='get_overtime'),
    # path('absences/', ListCreateAbsenceView.as_view(), name='absence'),
    # path('absences/<str:pk>/', RetUpdDesAbsenceAPIView.as_view(), name='get-absence'),
    # path('awards/', ListCreateAwardView.as_view(), name='award'),
    # path('awards<str:pk>/', RetUpdDesAwardView.as_view(), name='get-award'),
    # path('discounts/', ListCreateDicountView.as_view(), name='discount'),
    # path('discounts/<str:pk>/', RetUpdDesDicountView.as_view(), name='get-discount'),
    # path('advances/', ListCreateAdvanceView.as_view(), name='advances'),
    # path('advances/<str:pk>/', RetUpdDesAdvanceView.as_view(), name='get-advance'),
    # path('expences/', ListCreateExpenceView.as_view(), name='expendes'),
    # path('expences/<str:pk>/', RetUpdDesExpenceView.as_view(), name='get-expence'),
]
