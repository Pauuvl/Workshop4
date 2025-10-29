from django.contrib import admin
from django.urls import path, include
from movie import views

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', include('news.urls')),
    path('movies-chart/', views.movies_chart, name='movies_chart'),
    path('movies-chart-genre/', views.movies_chart_genre, name='movies_chart_genre'),
    path('signup/', views.signup, name='signup'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
