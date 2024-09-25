from django.shortcuts import render
from django.http import HttpResponse

def homePage(request):
    return HttpResponse('<h1>Hello Mr. Santosh and Ms. Sowmya shall we begin!</h1>')
