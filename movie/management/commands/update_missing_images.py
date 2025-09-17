import os
import requests
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import time

class Command(BaseCommand):
    help = "Generate only missing movie images using DALL-E API"

    def generate_and_download_image(self, client, movie_title, save_folder):
        """
        ✅ Función para generar y descargar imágenes
        """
        prompt = f"Professional movie poster style for {movie_title}, cinematic, high quality"
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        safe_title = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        image_filename = f"m_{safe_title}.jpg"
        image_path_full = os.path.join(save_folder, image_filename)

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
        else:
            self.stderr.write("Error: .env file not found")
            return

        api_key = os.environ.get('openai_apikey')
        if not api_key:
            self.stderr.write("Error: OpenAI API key not found")
            return

        client = OpenAI(api_key=api_key)
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        # ✅ Obtener solo películas sin imagen física
        movies = Movie.objects.all()
        success_count = 0
        error_count = 0

        for movie in movies:
            try:
                # ✅ Verificar si la imagen física ya existe
                safe_title = "".join(c for c in movie.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                expected_filename = f"m_{safe_title}.jpg"
                full_image_path = os.path.join(images_folder, expected_filename)
                
                if os.path.exists(full_image_path):
                    # ✅ Si la imagen existe, asignarla a la BD
                    movie.image = os.path.join('movie/images', expected_filename)
                    movie.save()
                    self.stdout.write(f"✓ Image assigned: {movie.title}")
                    continue
                
                # ✅ Si no existe, generarla
                self.stdout.write(f"🔄 Generating: {movie.title}")
                image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)
                movie.image = image_relative_path
                movie.save()
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Generated: {movie.title}"))
                time.sleep(3)
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f"❌ Error: {movie.title}: {str(e)}")
                continue

        self.stdout.write(self.style.SUCCESS(f"\nGenerated {success_count} new images, {error_count} errors"))