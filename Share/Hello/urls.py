from django.urls import path
# from .views import homePage

# urlpatterns = [
#     path('', homePage, name="homePage"),
# ]

from .views import homePage, aboutPage, SignupView, LoginView
urlpatterns = [
path('', homePage.as_view(), name='home'),
path('about', aboutPage.as_view(), name='about'),
path('signup/', SignupView.as_view(), name='signup'),
path('login/', LoginView.as_view(), name='login'),
]
