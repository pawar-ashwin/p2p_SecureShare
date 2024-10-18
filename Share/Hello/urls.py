# urls.py
from django.urls import path
from .views import HomePage, AboutPage, signup, user_dashboard, login, upload_view, download_view

urlpatterns = [
    path('', HomePage.as_view(), name='home'),
    path('user/', user_dashboard, name='user_dashboard'), 
    path('about/', AboutPage.as_view(), name='about'),
    path('login/', login, name='login'),
    path('signup/', signup, name='signup'),
    path('upload/', upload_view, name='upload'),
    path('download/', download_view, name='download'),
]
