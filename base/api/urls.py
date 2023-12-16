from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('auth/sign-up/' , SignUpView.as_view()),#####
    path('auth/log-in/', UserLoginApiView.as_view(), name='sign-in'),#####
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),#####
    path('auth/reset-password/' , ResetPasswordView.as_view(), name='reset-password'),####
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),#########
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),######
    path('test/' , test.as_view()),#####
    path('user/' , CurrentUserView.as_view()),######
    path('clients/' , ListCreateClient.as_view() , name="clients"),######post/get
    path('get-client/<str:pk>/' , RetUpdDesClient.as_view() , name="get-client"),
    path('products/' , listCreateProducts.as_view() , name="products"),######
    path('categories/' , ListCreateCategory.as_view() , name="categories"),##### post/get
    path('product/<str:pk>' , GetProduct.as_view() , name="product"),##### post/get
    path('employees/', ListCreateEmployee.as_view(), name='employee'),#### post/get
    path('get-employee/<str:pk>/', RetUpdDesEmployee.as_view(), name='get-employee'),#### get/post/delete  
    path('user_items/' , CartProductsView.as_view() , name="user_products"),
    path('cart/' , CartView.as_view()),
    path('get-number/', GetPhonenumberView.as_view(), name='get-number'),
    path('suppliers/' , ListCreateSupplier.as_view() , name="suppliers"), ##### post/get
    path('get-supplier/<str:pk>' , GetSupplier.as_view() , name="get-supplier"),##### post/get
    path('orders/' , ListCreateOrder.as_view() ,name="orders"),####
    path('create/' , CreateOrder.as_view() ),
    path('incomings/' , ListIncomings.as_view() , name="incomings"),
    path('create-incoming/' , CreateIncomingView.as_view()),
    path('incoming_product/' , CreateIncomingProducts.as_view() , name=""),
    path('bonuses/', ListCreateBonus.as_view(), name='bonuses'),####get/post
    path('get-bonus/<str:pk>/', RetUpdDesBonusView.as_view(), name='get-bonus'),####get/post/delete
    path('discounts/', ListCreateDicountView.as_view(), name='discount'),####get/post
    path('get-discount/<str:pk>/', RetUpdDesDicountView.as_view(), name='get-discount'),####get/post/delete
    path('overtimes/', ListCreatOverTimeView.as_view(), name='overtimes'),### post/get
    path('get-overtime/<str:pk>/', RetUpdDesOverTimeView.as_view(), name='get_overtime'), #####get/post/delete
    path('absences/', ListCreateAbsenceView.as_view(), name='absence'),####get/post
    path('get-absence/<str:pk>/', RetUpdDesAbsenceAPIView.as_view(), name='get-absence'),####get
    path('advances/', ListCreateAdvanceView.as_view(), name='advances'),####
    path('get-advance/<str:pk>/', RetUpdDesAdvanceView.as_view(), name='get-advance'),####
    path('expenses/', ListCreateExpense.as_view(), name='expendes'),
    path('get-expense/<str:pk>/', RetUpdDesExpense.as_view(), name='get-expense'),
    path('change-quantity/<str:pk>/<str:pk2>/' , Quantity_Handler.as_view() , name="quantity-handler"),
    path('add_to_cart/<str:pk>/<str:pk2>/' , Add_to_Cart.as_view() , name="add-to-cart")
    # path('salaries/' , ListCreateSalary.as_view() , name="salaries"),
    # path('get-salary/<str:pk>/' , RetUpdDesSalary.as_view() , name="get-salary")
]
