from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


from django.urls import path
from .views import *
urlpatterns = [
    path('sign-up/' ,SingupView.as_view(), name='sign-up'),
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
    path('get-product/<str:pk>/', GetUdpDesProductView.as_view()),
    path('suppliers/', ListCreateSupplierView.as_view(), name='suppliers'),
    path('get-supplier/<str:pk>/' , GetSupplier.as_view() , name="get-supplier"),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('points/', ListPointsView.as_view(), name='points'),
    path('orders/user/', ListOrdersUserView.as_view(), name='orders-user'),
    path('employees/', ListCreatEmployeeView.as_view(), name='employee'),
    path('employees/<str:pk>/', RetUpdDesEmployeeAPIView.as_view(), name='get-employee'),
    path('overtimes/', ListCreatOverTimeView.as_view(), name='overtimes'),
    path('overtimes/<str:pk>/', RetUpdDesOverTimeView.as_view(), name='get_overtime'),
    path('absences/', ListCreateAbsenceView.as_view(), name='absence'),
    path('absences/<str:pk>/', RetUpdDesAbsenceAPIView.as_view(), name='get-absence'),
    path('awards/', ListCreateAwardView.as_view(), name='award'),
    path('awards/<str:pk>/', RetUpdDesAwardView.as_view(), name='get-award'),
    path('discounts/', ListCreateDicountView.as_view(), name='discount'),
    path('discounts/<str:pk>/', RetUpdDesDicountView.as_view(), name='get-discount'),
    path('advances/', ListCreateAdvanceView.as_view(), name='advances'),
    path('advances/<str:pk>/', RetUpdDesAdvanceView.as_view(), name='get-advance'),
    path('sxtraexpences/', ListCreateExpenceView.as_view(), name='extra-expence'),
    path('extraexpences/<str:pk>/', RetUpdDesExpenceView.as_view(), name='get-extra-expence'),
    path('search/product/', SearchView.as_view(), name='search-product'),
    # path('incomings/', ListCreateIncomingView.as_view(), name='incoming'),
    # path('incoming-products/<int:id>/', CreateIncomingProductsView.as_view(), name='incoming-produc')
    # path('manual-reciepts/', ListCreateManualRecieptView.as_view(), name='manual-reciepts'),
    path('one/', ListManualRecieptProductsView.as_view()),
    path('add-product-to-cart/', ListCreateCartProduct.as_view(), name='add-pro-to-cart'),
    path('list-product-cart/<str:pk>/', DesUpdCartProducts.as_view(), name='list-product-cart'),
    path('create-medium/<str:order_id>/', CreateMediumView.as_view(), name='create-medium'),
    path('get-mediums/', ListMediumView.as_view(), name='list-medium'),
    path('medium-handler/<str:pk>/<str:pk2>/', Medium_Handler.as_view(), name='get-medium'),
    path('get-medium/<str:pk>/', GetMediumView.as_view(), name='get-medium'),
    path('create-receipt-output/', CreateReceiptOrdersView.as_view(), name='create-output'),
    path('get-receipt-output/<int:output_id>/', ListReceiptOutput.as_view(), name='get'),
    # path('get-outputs/', GetOutputs.as_view(), name='get-outputs'),

    # path('product/category/', UserListView.as_view()),
]
