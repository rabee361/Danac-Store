from django.shortcuts import render
from .models import Chat , ChatMessage



def TestChat(request):
    messages = ChatMessage.objects.filter(chat=1)
    context = {
        'messages':messages
    }
    return render(request,'base/test.html',context=context)
