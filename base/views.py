from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import render
from .models import Chat , ChatMessage



def TestChat(request):
    messages = ChatMessage.objects.filter(chat=1)
    context = {
        'messages':messages
    }
    return render(request,'base/test.html',context=context)
