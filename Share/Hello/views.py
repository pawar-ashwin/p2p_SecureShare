from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer, LoginSerializer

# def homePage(request):
#     return HttpResponse('<h1>Hello Mr. Santosh and Ms. Sowmya shall we begin!</h1>')

class homePage(TemplateView):
    template_name = 'home.html'

class aboutPage(TemplateView):
    template_name = 'about.html'
    
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)