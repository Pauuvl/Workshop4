from django.shortcuts import render
from .models import News

def news_list(request):
    news = News.objects.all().order_by('-date')
    return render(request, 'news/news.html', {'news': news})
