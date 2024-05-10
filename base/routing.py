from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>\d+)/(?P<user_id>\d+)$", consumers.CreateEmployeeMessage.as_asgi()),
    re_path(r"ws/driver-chat/(?P<chat_id>\d+)/(?P<user_id>\d+)$", consumers.CreateDriverMessage.as_asgi()),
]
