from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

from io import BytesIO

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {
        'searchTerm': searchTerm,
        'movies': movies,
        'name': 'Paulina Velasquez'
    })

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = None
    if request.method == "POST":
        email = request.POST.get("email")
    return render(request, "signup.html", {"email": email})

def movies_chart(request):
    movies_by_year = Movie.objects.values('year').order_by('year')
    years = [m['year'] for m in movies_by_year]
    counts = [Movie.objects.filter(year=m['year']).count() for m in movies_by_year]

    plt.figure(figsize=(6,4))
    plt.bar(years, counts, color='skyblue')
    plt.xlabel("Año")
    plt.ylabel("Cantidad de Películas")
    plt.title("Películas por Año")
    plt.xticks(rotation=45)

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')

def movies_chart_genre(request):
    movies = Movie.objects.all()
    genre_counts = {}
    for movie in movies:
        if movie.genre:
            first_genre = movie.genre.split(',')[0].strip()
            genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1

    genres = list(genre_counts.keys())
    counts = list(genre_counts.values())

    plt.figure(figsize=(6,4))
    plt.bar(genres, counts, color='lightcoral')
    plt.xlabel("Género")
    plt.ylabel("Cantidad de Películas")
    plt.title("Películas por Género (primer género)")
    plt.xticks(rotation=45, ha="right")

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type='image/png')
