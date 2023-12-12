from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


urlpatterns = [
    path('sign-up/' , SignupView.as_view()),
    path('test/' , test.as_view()),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('user/' , CurrentUserView.as_view()),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('sign-in/', UserLoginApiView.as_view(), name='sign-in'),
    path('products/' , listProducts.as_view() , name="products"),
    path('categories/' , ListCategory.as_view() , name="categories"),
    path('product/<str:pk>' , GetProduct.as_view() , name="product"),
    path('user_items/' , CartProducts.as_view() , name="user_products")
    # path('remove-item/<str:pk>' , remove_from_cart , name="remove-item"),
    # path('add-to-cart/<str:pk>' , add_to_cart, name="add-to-cart"),
    # path('quantity_handler/<str:pk>/<str:pk2>' , QuantityHandlerView.as_view(), name="quantity_handler"),

]
