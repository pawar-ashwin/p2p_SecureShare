# urls.py

from django.urls import path
from .views import HomePage, AboutPage, signup, user_dashboard, login, user_profile, update_email, update_share_path

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('user/', user_dashboard, name='user_dashboard'), 
    path('about/', AboutPage.as_view(), name='about'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('profile/', user_profile, name='user_profile'),
    path('update_share_path/', update_share_path, name='update_share_path'),
    path('update_email/', update_email, name='update_email'),  # New path for updating email
]
