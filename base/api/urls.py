from django.urls import path
from .views import *
from rest_framework_simplejwt import views as jwt_views


from django.urls import path
from .views import *
urlpatterns = [
    path('sign-up/' , SignupView.as_view()),
    path('test/' , test.as_view()),
    path('sign-in/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutAPIView.as_view())
]
