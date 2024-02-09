from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import render


class TestChat(APIView):
    def get(self,request):
        return render(request,'base/test.html')


