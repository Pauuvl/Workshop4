from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt

from io import BytesIO
import numpy as np
from django.shortcuts import render
from openai import OpenAI
from dotenv import load_dotenv
from .models import Movie
import os

# ✅ Cargar variables de entorno
load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def cosine_similarity(a, b):
    """Calcula la similitud del coseno entre dos vectores"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding(text):
    """Obtiene el embedding de un texto usando OpenAI"""
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def movie_recommendation(request):
    """
    ✅ Vista principal del sistema de recomendación
    Recibe un prompt del usuario y encuentra la película más similar
    """
    recommendation = None
    similarity_score = 0
    search_query = ""
    error = None
    
    if request.method == 'POST':
        search_query = request.POST.get('prompt', '').strip()
        
        if search_query:
            try:
                # ✅ Generar embedding del prompt del usuario
                prompt_emb = get_embedding(search_query)
                
                # ✅ Buscar la película más similar en la base de datos
                best_movie = None
                max_similarity = -1
                
                for movie in Movie.objects.all():
                    # ✅ Convertir el campo binario de vuelta a array numpy
                    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                    
                    # ✅ Calcular similitud
                    similarity = cosine_similarity(prompt_emb, movie_emb)
                    
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_movie = movie
                
                recommendation = best_movie
                similarity_score = max_similarity
                
            except Exception as e:
                error = f"Error al procesar la recomendación: {str(e)}"
        else:
            error = "Por favor ingresa una descripción para buscar"
    
    context = {
        'recommendation': recommendation,
        'similarity_score': similarity_score,
        'search_query': search_query,
        'error': error
    }
    
    return render(request, 'movie/recommendation.html', context)

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
