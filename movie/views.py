from django.shortcuts import render
from django.http import HttpResponse


def home(request):

    return render(request, 'home.html',{'name':'Paulina Velasquez L'})

def about(request):
    return render(request, 'about.html')


# Create your views here.
