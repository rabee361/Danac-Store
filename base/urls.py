from .views import *
from django.urls import path

urlpatterns = [
    path('test/' , TestChat , name="test"),
]