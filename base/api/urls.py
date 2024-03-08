from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    # path('get-code/', GetPhonenumberView.as_view(), name='get-code'),
    # path('verify-code-password/', VerifyCodeToChangePassword.as_view()),
    # path('get-number/', GetPhonenumberView.as_view(), name='get-number'),
    # path('change-image/<str:user_pk>/' , UpdateImageUserView.as_view(), name="change-view"),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('firebase-token/refresh/',RefreshFirebaseToken.as_view(),name="refresh-firebase-token"),
    path('auth/sign-up/' , SignUpView.as_view()),
    path('auth/log-in/', UserLoginApiView.as_view(), name='sign-in'),
    path('auth/logout/', LogoutAPIView.as_view(), name='logout'),
    path('auth/reset-password/<str:user_id>/' , ResetPasswordView.as_view(), name='reset-password'),
    path('verify-code/', VerefyPhonenumberView.as_view(), name='verify-code'),

    path('notifications/', GetNotificationView.as_view()),
    path('settings/<str:pk>/', ListInformationUserView.as_view(), name='settings'),
    path('settings/update-image/<str:user_pk>/', UpdateImageUserView.as_view(), name='update-image'),

    path('update-location/' , UpdateLocationView.as_view() , name="update-location"),
    path('get-location/<str:employee_id>/' , GetSalesEmployeeLocation.as_view() , name="get-location"),

    path('chats/' , Chats.as_view()),#### new
    path('get-chat/<str:pk>/', GetChat.as_view() , name="get-chat"),
    path('chat-messages/<str:chat_id>/', ChatMessages.as_view()), #### new
    path('send-message/<str:chat_id>/<str:user_id>/' , SendMessage.as_view()),

    path('states/' , States.as_view() , name="states"),
    path('get-state/' , GetState.as_view() , name="get-state"),

    path('clients/' , ListCreateClient.as_view() , name="clients"),
    path('get-client/<str:pk>/' , RetUpdDesClient.as_view() , name="get-client"),
    path('client-info/<str:pk>/' , Client_Details.as_view(), name="client-info"),
    path('client-orders/' , ListClientOrders.as_view() , name="client-orders"),

    path('total-points/', TotalClientPointsView.as_view(), name='total-points'),
    path('used-points/', UsedClientPointsView.as_view(), name='used-points'),
    path('expired-points/', ExpiredClientPointsView.as_view(), name='expired-points'),
    path('points/', ClientPointsView.as_view(), name='client-points'),
    
    path('products/' , listCreateProducts.as_view() , name="products"),
    path('special-products/' , SpecialProducts.as_view() , name="special-products"),
    path('ads/' , ListAds.as_view() , name="list-ads"),
    path('get-product/<str:pk>/' , RetUpdDesProduct.as_view() , name="product"),
    path('categories/' , ListCreateCategory.as_view() , name="categories"),
    path('get-category/<str:pk>/' , RetUpdDesCategory.as_view() , name="get-category"),
    path('product-types/' ,ListCreateProductType.as_view(), name="product-types"), ##### new
    path('get-product-type/<str:pk>/' , RetUpdDesProductType.as_view() , name="get-product-type"),#### new
    path('total-categories/' , GetTotalCategories.as_view()),
    path('total-product-types/', GetTotalProductTypes.as_view()),
    
    path('cart_items/<str:pk>' , Cart_Items.as_view() , name="cart_products"),
    path('cart_details/<str:pk>' , Cart_Items_Details.as_view() , name="cart_products_details"),
    path('create-order/<str:cart_id>/' , CreateOrderView.as_view() , name="create-order"),
    path('change-quantity/<str:pk>/<str:pk2>/' , Quantity_Handler.as_view() , name="quantity-handler"), 
    path('add_to_cart/<str:pk>/<str:pk2>/' , Add_to_Cart.as_view() , name="add-to-cart"),
    path('delete-item/<str:pk>/' , Delete_From_Cart.as_view() , name="delete-item"),

    path('suppliers/' , ListCreateSupplier.as_view() , name="suppliers"),
    path('get-supplier/<str:pk>/' , GetSupplier.as_view() , name="get-supplier"),
    path('orders/' , ListOrders.as_view() ,name="orders"),
    path('order/<str:pk>/' , GetOrder.as_view() , name="get-order"),
    path('reject-order/<str:pk>/' , DeleteOrder.as_view() , name="delete-order"),

    path('employees/', ListCreateEmployee.as_view(), name='employee'),
    path('get-employee/<str:pk>/', RetUpdDesEmployee.as_view(), name='get-employee'),

    path('sales-employees/' , SalesEmployee.as_view() , name="sale-employees"),
    path('get-sales-employee/<str:pk>' , RetSalesEmployee.as_view() , name="get-sales-employee"),

    path('bonuses/', ListCreateBonus.as_view(), name='bonuses'),
    path('get-bonus/<str:pk>/', RetUpdDesBonus.as_view(), name='get-bonus'),
    path('discounts/', ListCreateDicount.as_view(), name='discount'),
    path('get-discount/<str:pk>/', RetUpdDesDicount.as_view(), name='get-discount'),
    path('overtimes/', ListCreatOverTime.as_view(), name='overtimes'),
    path('get-overtime/<str:pk>/', RetUpdDesOverTime.as_view(), name='get_overtime'),
    path('absences/', ListCreateAbsence.as_view(), name='absence'),
    path('get-absence/<str:pk>/', RetUpdDesAbsence.as_view(), name='get-absence'),
    path('advances/', ListCreateAdvance.as_view(), name='advances'),
    path('get-advance/<str:pk>/', RetUpdDesAdvance.as_view(), name='get-advance'),
    path('extra-expenses/', ListCreateExtraExpense.as_view(), name='expenses'),
    path('get-extra-expense/<str:pk>/', RetUpdDesExtraExpense.as_view(), name='get-expense'),
    path('employee_salary/<str:pk>/', RetUpdDesSalary.as_view()),
    path('salaries/' , ListCreateSalary.as_view() , name="create-salary"),
    path('employee-salary-info/<str:pk>' , GetSalaryEmployee.as_view() , name="salary-info"), 

    path('supplier-debts/' , ListCreateSupplierDebts.as_view() , name="supplier-debts"),
    path('client-debts/' , ListCreateClientDebts.as_view() , name="client-debts"),
    path('debt-for-client/<str:pk>/' , GetClientDebt.as_view()),
    path('get-client-debt/<str:pk>/' , RetUpdDesClientDebt.as_view() , name="client-debt"),
    path('debt-for-supplier/<str:pk>/' , GetSupplierDebt.as_view()),
    path('get-supplier-debt/<str:pk>/' , RetUpdDesSupplierDebt.as_view() , name="supplier-debt"),
    path('get-registry/' , ListRegistries.as_view() , name="list-registries"),
    path('deposites/' , ListCreateDeposite.as_view() , name="deposites"),
    path('get-deposite/<str:pk>/' , RetUpdDesDeposite.as_view() , name="get-deposite"),
    path('withdraws/' , ListCreateWithDraw.as_view() , name="withdraws"),
    path('get-withdraw/<str:pk>/' , RetUpdDesWithDraw.as_view() , name="get-withdraw"),
    path('payments/' , ListCreatePayment.as_view() , name="payments"),
    path('get-payment/<str:pk>/' , RetUpdDesPayment.as_view() , name="get-payment"),
    path('recieved-payments/' , ListCreateRecievedPayment.as_view() , name="payments"),
    path('get-recieved-payment/<str:pk>/' , RetUpdDesRecievedPaymnt.as_view() , name="get-payment"),
    path('expenses/' , ListCreateExpense.as_view() , name="expenses"),
    path('get-expense/<str:pk>/' , RetUpdDesExpense.as_view() , name="get-expense"),
    path('operation-info/',GetRegistryOperations.as_view(),name="operation-info"),

    path('returned-supplier-package/',ListReturnedSupplierPackages.as_view()),### new
    path('get-package-supplier/<str:pk>/',RetReturnedSupplierPackages.as_view()), #### new
    path('returned-goods-supplier/', ListCreateRetGoodsSupplier.as_view()),
    path('get-returned-supplier/<str:pk>/', RetUpdDesReturnGoodSupplier.as_view()),###### delete

    path('returned-client-package/',ListReturnedClientPackages.as_view()),##### new
    path('get-package-client/<str:pk>/',RetReturnedClientPackages.as_view()),#### new
    path('returned-goods-client/', ListCreateRetGoodsClient.as_view()),
    path('get-returned-client/<str:pk>/', RetUpdDesReturnGoodClient.as_view()),

    path('damaged-packages/',ListDamagedPackages.as_view()),##### new
    path('get-damaged-package/<str:pk>/',RetDamagedPackages.as_view()),#### new
    path('damaged-product/', ListCreateDamagedProduct.as_view()),
    path('get-damaged-product/<str:pk>/', RetUpdDesDamagedProduct.as_view()),

    path('get-receipt-manual/<str:pk>/', GetManualReceipt.as_view(), name="get-manuals"),
    path('freeze-manual/<str:receipt_id>/' , FreezeManualReceipt.as_view(),name="freeze-manual"),
    path('unfreeze-manual/<str:receipt_id>/' , UnFreezeManualReceipt.as_view(),name="funreeze-manual"),
    path('create-manual-receipt/<str:medium_id>/',CreateManualReceiptView.as_view()),
    path('list-manuals/' , ListManualReceipt.as_view() , name="list-manual"),
    path('list-frozen-manual/' , ListFrozenManualReceipts.as_view()),
    path('update-manual/<str:pk>/' , UpdateManualReceipt.as_view() , name="update-manual"),
    path('get-manual-product/<str:pk>/' , RetUpdDesManualReceiptProduct.as_view()),
    path('create-manual-product/' , CreateManualProduct.as_view()),
 
    path('get-receipt-output/<str:pk>/', GetOutput.as_view(), name='get-output'),
    path('freeze-output/<str:receipt_id>/' , FreezeOutputReceipt.as_view(),name="freeze-output"),
    path('unfreeze-output/<str:receipt_id>/' , UnFreezeOutputReceipt.as_view(),name="funreeze-output"),
    path('create-output-receipt/<int:medium_id>/', ReceiptOrdersView.as_view()),
    path('list-outputs/' , ListOutputs.as_view() , name="list-outputs"),
    path('list-frozen-outputs/' , ListFrozenOutputReceipts.as_view()),
    path('update-output/<str:pk>/' , UpdateOutputReceipt.as_view() , name="update-output"),
    path('get-output-product/<str:pk>/' , RetUpdDesOutputProduct.as_view()),
    path('create-output-product/' , CreateOutputProduct.as_view()),
 
    path('get-receipt-incoming/<str:pk>/' , GetIncoming.as_view() , name="get-incoming"),
    path('freeze-incoming/<str:receipt_id>/' , FreezeIncomingReceipt.as_view(),name="freeze-incoming"),
    path('unfreeze-incoming/<str:receipt_id>/' , UnFreezeIncomingReceipt.as_view(),name="funreeze-incoming"),
    path('create-incoming/<str:medium_id>/', CreateIncomingView.as_view()),
    path('list-incoming/' , ListIncomings.as_view() , name="list-incomings"),
    path('list-frozen-incoming/' , ListFrozenIncomingReceipts.as_view()),
    path('update-incoming/<str:pk>/' , UpdateIncomingReceipt.as_view() , name="update-incoming"),
    path('get-incoming-product/<str:pk>/' , RetUpdDesIncomingProduct.as_view()),
    path('create-incoming-product/' , CreateIncomingProduct.as_view()),
 
    path('list-medium-products/<str:medium_id>/',  ListMediumView.as_view()),
    path('update-product-medium/<str:pk>/', UpdateProductsMedium.as_view()),
    path('add-order-to-medium/<str:order_id>/', CreateMediumForOrderView.as_view()),
    path('create-medium/', CreateMedium.as_view()),
    path('add-to-medium/<str:medium_id>/<str:product_id>/', Add_To_Medium.as_view()),
    path('delete-product-from-medium/<str:pk>/', DeleteProductsMediumView.as_view()),
    path('add-product-to-medium/' , Add_product_to_Medium.as_view()),
    path('delete-medium/<str:pk>/' , RetDesMedium.as_view() , name="delete-medium"),

    path('create-delivery-arrived/<str:pk>/', ListCreateDeliveryArrived.as_view()),
    path('get-delivery-arrived/', ListCreateDeliveryArrived.as_view()),
    path('get-delivery-arrived-for-employee/<str:state>/', DelevaryArrivedForEmployee.as_view()),
    path('get/<str:pk>/', GetDelevaryArrivedForEmployee.as_view()),
    path('accept-delevary-arrived/<str:pk>/', AcceptDelevaryArrived.as_view()),

    path('create-medium-two/', CreateMediumTwo.as_view(), name="create-mediumtwo"),
    path('add-to-medium-two/<str:mediumtwo_id>/<str:product_id>/', AddToMediumTwo.as_view(), name="add-to-mediumtwo"),
    path('medium-two-handler/<str:mediumtwo_id>/<str:pk2>/', MediumTow_Handler.as_view()),
    path('delete-product-from-medium-two/<str:pk>/', DesMediumTwo.as_view()),
    path('create-order-envoy/<str:mediumtwo_id>/', CreateOrderEnvoyView.as_view()),
    path('list-order-envoy/<str:pk>/', ListOrderEnvoy.as_view()),
    path('delete-medium-two/<str:pk>/' , DeleteMediumTwo.as_view()),
    path('list-medium-two-products/<str:medium2_id>/' , ListMediumTwoProducts.as_view())
    
    ]