import os
import re
from django.core.management.base import BaseCommand
from movie.models import Movie
from pathlib import Path

class Command(BaseCommand):
    help = "Update movie images from existing folder"

    def normalize_title(self, title):
        """
        Normaliza el título para que coincida con el nombre del archivo
        """
        # Remover caracteres especiales y convertir a minúsculas
        normalized = re.sub(r'[^\w\s-]', '', title.lower())
        # Reemplazar espacios con guiones bajos
        normalized = normalized.replace(' ', '_')
        # Remover múltiples guiones bajos
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip('_')

    def find_matching_image(self, movie_title, image_files):
        """
        Busca la imagen que mejor coincida con el título de la película
        """
        normalized_title = self.normalize_title(movie_title)
        
        # Primero intenta coincidencia exacta
        for filename in image_files:
            if normalized_title in self.normalize_title(filename):
                return filename
        
        return None

    def handle(self, *args, **kwargs):
        # 📂 Ruta de la carpeta de imágenes
        images_folder = 'media/movie/images/'
        
        # ✅ Verificar si la carpeta existe
        if not os.path.exists(images_folder):
            self.stderr.write(f"Error: Images folder not found at {images_folder}")
            self.stderr.write("Please download and extract the images to this folder")
            return

        # ✅ Contadores
        updated_count = 0
        not_found_count = 0

        # ✅ Obtener todas las películas
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in database")
        
        # ✅ Obtener lista de archivos en la carpeta de imágenes (solo .jpg)
        image_files = [f for f in os.listdir(images_folder) if f.endswith(('.jpg'))]
        self.stdout.write(f"Found {len(image_files)} JPG images in folder")
        
        # ✅ Recorrer todas las películas
        for movie in movies:
            try:
                # ✅ Buscar imagen que coincida
                matching_image = self.find_matching_image(movie.title, image_files)
                
                if matching_image:
                    # ✅ Actualizar la imagen en la base de datos
                    image_path = os.path.join('movie/images', matching_image)
                    movie.image = image_path
                    movie.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Image found: {movie.title} -> {matching_image}"))
                else:
                    not_found_count += 1
                    self.stdout.write(f"✗ Image not found: {movie.title}")
                    
            except Exception as e:
                self.stderr.write(f"Error processing {movie.title}: {str(e)}")
                continue

        # ✅ Mostrar resumen final
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("UPDATE SUMMARY:"))
        self.stdout.write(self.style.SUCCESS(f"Movies processed: {movies.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Images updated: {updated_count}"))
        self.stdout.write(self.style.ERROR(f"Images not found: {not_found_count}"))
        self.stdout.write(self.style.SUCCESS("="*60))
        
        if not_found_count > 0:
            self.stdout.write(self.style.NOTICE("\n💡 Algunas imágenes no se encontraron."))
            self.stdout.write(self.style.NOTICE("📥 Asegúrate de tener todas las imágenes JPG en media/movie/images/"))
