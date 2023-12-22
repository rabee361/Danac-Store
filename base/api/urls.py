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

    path('clients/' , ListCreateClient.as_view() , name="clients"),######
    path('get-client/<str:pk>/' , RetUpdDesClient.as_view() , name="get-client"),########
    path('products/' , listCreateProducts.as_view() , name="products"),######
    path('special-products/' , SpecialProducts.as_view() , name="special-products"),######
    path('get-product/<str:pk>/' , RetUpdDesProduct.as_view() , name="product"),##### 
    path('categories/' , ListCreateCategory.as_view() , name="categories"),##### 
    path('get-category/<str:pk>/' , RetUpdDesCategory.as_view() , name="get-category"),##### 
    path('employees/', ListCreateEmployee.as_view(), name='employee'),######
    path('get-employee/<str:pk>/', RetUpdDesEmployee.as_view(), name='get-employee'),####  
    path('user_items/' , CartProductsView.as_view() , name="user_products"),#### 
    path('cart/' , CreateCartView.as_view()),##### 
    path('create-order/<str:cart_id>/' , CreateOrderView.as_view() , name="create-order"),#### 
    path('change-quantity/<str:pk>/<str:pk2>/' , Quantity_Handler.as_view() , name="quantity-handler"), #### 
    path('add_to_cart/<str:pk>/<str:pk2>/' , Add_to_Cart.as_view() , name="add-to-cart"),##### 
    path('get-number/', GetPhonenumberView.as_view(), name='get-number'),
    path('suppliers/' , ListCreateSupplier.as_view() , name="suppliers"), #######
    path('get-supplier/<str:pk>/' , GetSupplier.as_view() , name="get-supplier"),######
    path('orders/' , ListOrders.as_view() ,name="orders"),#######
    # path('create/' , CreateOrder.as_view() ),

    path('bonuses/', ListCreateBonus.as_view(), name='bonuses'),#######
    path('get-bonus/<str:pk>/', RetUpdDesBonusView.as_view(), name='get-bonus'),######
    path('discounts/', ListCreateDicountView.as_view(), name='discount'),######
    path('get-discount/<str:pk>/', RetUpdDesDicountView.as_view(), name='get-discount'),######
    path('overtimes/', ListCreatOverTimeView.as_view(), name='overtimes'),#######
    path('get-overtime/<str:pk>/', RetUpdDesOverTimeView.as_view(), name='get_overtime'), #######
    path('absences/', ListCreateAbsenceView.as_view(), name='absence'),######
    path('get-absence/<str:pk>/', RetUpdDesAbsenceAPIView.as_view(), name='get-absence'),#######
    path('advances/', ListCreateAdvanceView.as_view(), name='advances'),#######
    path('get-advance/<str:pk>/', RetUpdDesAdvanceView.as_view(), name='get-advance'),######
    path('extra-expenses/', ListCreateExtraExpense.as_view(), name='expenses'),######
    path('get-extra-expense/<str:pk>/', RetUpdDesExtraExpense.as_view(), name='get-expense'),#####
    path('employee_salary/<int:employee_id>/', GetSalaryEmployee.as_view()),########## 
    path('salaries/' , ListCreateSalary.as_view() , name="create-salary"),######## 

    path('supplier-debts/' , ListCreateSupplierDebts.as_view() , name=""),######## 
    path('client-debts/' , ListCreateClientDebts.as_view() , name=""),########### 
    path('get-client-debt/<str:pk>/' , RetUpdDesClientDebt.as_view() , name="client-debt"),######## 
    path('get-supplier-debt/<str:pk>/' , RetUpdDesSupplierDebt.as_view() , name="supplier-debt"),######## 
    path('get-registry/' , GetRegistry.as_view() , name="registry"),##########
    path('deposites/' , ListCreateDeposite.as_view() , name="deposites"),######## 
    path('get-deposite/<str:pk>/' , RetUpdDesDeposite.as_view() , name="get-deposite"),######## 
    path('withdraws/' , ListCreateWithDraw.as_view() , name="withdraws"),########
    path('get-withdraw/<str:pk>/' , RetUpdDesWithDraw.as_view() , name="get-withdraw"), #######
    path('payments/' , ListCreatePayment.as_view() , name="payments"),######
    path('get-payment/<str:pk>/' , RetUpdDesPayment.as_view() , name="get-payment"), #######
    path('recieved-payments/' , ListCreateRecievedPayment.as_view() , name="payments"),###### 
    path('get-recieved-payment/<str:pk>/' , RetUpdDesRecievedPaymnt.as_view() , name="get-payment"),######

    path('returned-goods-supplier/', ListCreateRetGoodsSupplier.as_view()),##### 
    path('get-returned-supplier/<str:pk>/', RetUpdDesReturnGoodSupplier.as_view()), ##### 
    path('returned-goods-client/', ListCreateRetGoodsClient.as_view()), ##### 
    path('get-returned-client/<str:pk>/', RetUpdDesReturnGoodClient.as_view()), #### 

    path('damaged-product/', ListCreateDamagedProduct.as_view()),####### 
    path('get-damaged-product/<str:pk>/', RetUpdDesDamagedProduct.as_view()),##### 


    path('get-receipt-output/<int:output_id>/', GetOutput.as_view(), name='get-output'),##### new
    path('create-output-receipt/<int:medium_id>/', ReceiptOrdersView.as_view()), #### new
    path('list-outputs/' , ListOutputs.as_view() , name="list-outputs"),##### new

    path('get-receipt-incoming/<str:pk>/' , GetIncoming.as_view() , name="get-incoming"),##### new
    path('create-incoming/<str:medium_id>/', CreateIncomingView.as_view()),#### new
    path('list-incoming/' , ListIncomings.as_view() , name="list-incomings"),##### new

    path('list-medium-products/<str:medium_id>/', ListMediumView.as_view()),######
    path('update-product-medium/<str:pk>/', UpdateProductsMedium.as_view()),#### 
    path('add-order-to-medium/<str:order_id>/', CreateMediumForOrderView.as_view()),###### 
    path('create-medium/', CreateMedium.as_view()),##### 
    path('add-to-medium/<str:medium_id>/<str:product_id>/', Add_To_Medium.as_view()),####
    path('medium-handler-quantity/<str:pk>/<str:pk2>/', Medium_Handler.as_view()),####
    path('delete-medium/<str:pk>/' , RetDesMedium.as_view() , name="delete-medium"),#### 

    path('get-receipt-manual/<str:medium_id>/', GetManualReceipt.as_view(), name="list-manuals"),##### new
    path('create-manual-receipt/<str:medium_id>/',CreateManualReceiptView.as_view()),#### new
    path('list-manuals/' , ListManualReceipt.as_view() , name="list-manual"),##### new

    path('create-delivery-arrived/<str:pk>/', ListCreateDeliveryArrived.as_view()),
    path('get-delivery-arrived/', ListCreateDeliveryArrived.as_view()),

    path('list-outputs/' , ListOutputs.as_view()),



    ]

