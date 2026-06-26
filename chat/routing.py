from django.urls import path

from .consumer import ChatConsumer

websocket_urlpatterns = [
    path("ws/startups/<uuid:startup_id>/chat/", ChatConsumer.as_asgi()),
]
