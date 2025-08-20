from django.core.management.base import BaseCommand
from movie.models import Movie
import os
import json

class Command(BaseCommand):
    help = 'Carga 100 películas desde movies.json en la base de datos'

    def handle(self, *args, **kwargs):
        # Ruta del archivo JSON
        json_file_path = os.path.join(
            os.path.dirname(__file__), "movies.json"
        )

        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f"❌ No se encontró {json_file_path}"))
            return

        # Leer JSON
        with open(json_file_path, "r", encoding="utf-8") as file:
            movies = json.load(file)

        cargadas = 0
        for i in range(min(100, len(movies))):
            movie = movies[i]

            title = movie.get("title", "Sin título")
            description = movie.get("description") or movie.get("plot") or "Descripción no disponible"
            genre = movie.get("genre", "Desconocido")
            year = movie.get("year") or 2000  # valor por defecto si no viene año

            exist = Movie.objects.filter(title=title).first()
            if not exist:
                Movie.objects.create(
                    title=title,
                    description=description,
                    genre=genre,
                    year=year,
                    image="movie/images/default.jpg"
                )
                cargadas += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {cargadas} películas cargadas correctamente"))
