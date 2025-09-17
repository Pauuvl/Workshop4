import os
import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

# ✅ Cargar variables de entorno
load_dotenv('openAI.env')

# ✅ Inicializar el cliente de OpenAI
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def get_embedding(text):
    """Obtiene el embedding de un texto usando OpenAI"""
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

class Command(BaseCommand):
    help = "Generate and store embeddings for ALL movies"

    def handle(self, *args, **kwargs):
        # ✅ Verificar API key
        if not os.environ.get('openai_apikey'):
            self.stderr.write("Error: OpenAI API key not found")
            return

        # ✅ Obtener todas las películas
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")
        
        updated_count = 0
        error_count = 0
        
        for movie in movies:
            try:
                # ✅ Verificar si ya tiene un embedding (no es el default)
                current_emb = np.frombuffer(movie.emb, dtype=np.float32)
                default_emb = np.zeros(1536, dtype=np.float32)
                
                # Si el embedding actual es diferente del default, saltar
                if not np.array_equal(current_emb, default_emb):
                    self.stdout.write(f"⚠️  Skipping (already has embedding): {movie.title}")
                    continue
                
                # ✅ Generar embedding de la descripción
                self.stdout.write(f"🔄 Processing: {movie.title}")
                embedding = get_embedding(movie.description)
                
                # ✅ Convertir a binario y guardar
                movie.emb = embedding.tobytes()
                movie.save()
                
                updated_count += 1
                self.stdout.write(f"✅ Embedding stored for: {movie.title}")
                
                # ⚠️ PEQUEÑA PAUSA para evitar rate limits (pero NO break)
                import time
                time.sleep(1)  # 1 segundo de pausa entre requests
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f"❌ Error processing {movie.title}: {str(e)}")
                continue

        self.stdout.write(self.style.SUCCESS(f"\n🌟 Finished processing!"))
        self.stdout.write(f"✅ Embeddings generated: {updated_count}")
        self.stdout.write(f"❌ Errors: {error_count}")
        self.stdout.write(f"📊 Total movies: {movies.count()}")