import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from messaging.routing import websocket_urlpatterns

from channels.auth import AuthMiddlewareStack
from django.urls import path
from messaging import consumers



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Share.settings")



django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<str:room_name>/", consumers.ChatConsumer.as_asgi()),
        ])
    ),
})
