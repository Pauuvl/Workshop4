import os
import requests
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time

class Command(BaseCommand):
    help = "Generate and update movie images using DALL-E API"

    def generate_and_download_image(self, client, movie_title, save_folder):
        """
        ✅ Función auxiliar que genera y descarga la imagen usando la API de DALL-E
        """
        prompt = f"Professional movie poster style for {movie_title}, cinematic, high quality"
        
        # ✅ Generar la imagen con DALL-E 3
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # ✅ Crear nombre de archivo seguro
        safe_title = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_filename = f"m_{safe_title}.jpg"  # Cambiado a JPG
        image_path_full = os.path.join(save_folder, image_filename)

        # ✅ Descargar y guardar la imagen
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        
        with open(image_path_full, 'wb') as f:
            f.write(image_response.content)

        return os.path.join('movie/images', image_filename)

    def handle(self, *args, **kwargs):
        # ✅ Cargar variables de entorno
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        env_path = base_dir / 'openAI.env'
        
        if env_path.exists():
            load_dotenv(env_path)
            self.stdout.write(f"Loaded .env file from: {env_path}")
        else:
            self.stderr.write(f"Error: .env file not found at {env_path}")
            return

        # ✅ Obtener la API key
        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write("Error: OpenAI API key not found")
            return

        # ✅ Inicializar el cliente
        client = OpenAI(api_key=api_key)

        # ✅ Crear carpeta de imágenes
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        # ✅ Procesar películas
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        # ✅ Contadores
        success_count = 0
        error_count = 0

        for movie in movies:
            try:
                # ✅ Verificar si ya tiene imagen
                if movie.image:
                    self.stdout.write(f"⚠️ Skipping (already has image): {movie.title}")
                    continue
                
                self.stdout.write(f"🔄 Processing: {movie.title}")
                
                # ✅ Generar y descargar la imagen
                image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)
                
                # ✅ Actualizar la imagen en la base de datos
                movie.image = image_relative_path
                movie.save()
                
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Saved image for: {movie.title}"))
                
                # ⚠️ Pequeña pausa para evitar rate limits
                time.sleep(2)
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f"❌ Error processing {movie.title}: {str(e)}")
                continue

        # ✅ Mostrar resumen final
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("GENERATION SUMMARY:"))
        self.stdout.write(self.style.SUCCESS(f"Movies processed: {movies.count()}"))
        self.stdout.write(self.style.SUCCESS(f"Images generated: {success_count}"))
        self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))
        self.stdout.write(self.style.SUCCESS("="*60))