from django.urls import path

from django.urls import path
from .views import *
urlpatterns = [
    path('sign-up/', StudentSignupView.as_view())
]
