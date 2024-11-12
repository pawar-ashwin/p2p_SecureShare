# urls.py

from django.urls import path
from .views import HomePage, AboutPage, signup, user_dashboard, login, user_profile, update_email, update_share_path, my_files, search_files, request_file, chat_view, send_message, file_requests, signout
from messaging.views import chat_room

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('user/', user_dashboard, name='user_dashboard'), 
    path('about/', AboutPage.as_view(), name='about'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('signout/', signout, name='signout'),
    path('profile/', user_profile, name='user_profile'),
    path('update_share_path/', update_share_path, name='update_share_path'),
    path('update_email/', update_email, name='update_email'),  # New path for updating email
    path('my-files/', my_files, name='my_files'),
    path('search_files/', search_files, name='search_files'),
    path('request_file/', request_file, name='request_file'),
    path('file_requests/', file_requests, name='file_requests'),
    path('chat/<str:username>/', chat_room, name='chat'),
    path('send_message/', send_message, name='send_message'),
]
