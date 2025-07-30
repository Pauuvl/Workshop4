from django.shortcuts import render
from django.http import HttpResponse


def home(request):

    return render(request, 'home.html',{'name':'Paulina Velasquez'})

def about(request):
    return HttpResponse("This is the About Page")


# Create your views here.
