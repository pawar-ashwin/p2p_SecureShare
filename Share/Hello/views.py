from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

# def homePage(request):
#     return HttpResponse('<h1>Hello Mr. Santosh and Ms. Sowmya shall we begin!</h1>')

class homePage(TemplateView):
    template_name = 'home.html'

class aboutPage(TemplateView):
    template_name = 'about.html'
