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
    """
    ✅ Obtiene el embedding de un texto usando OpenAI
    """
    response = client.embeddings.create(
        input=[text],
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def cosine_similarity(a, b):
    """
    ✅ Calcula la similitud del coseno entre dos vectores
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class Command(BaseCommand):
    help = "Calculate movie similarities using OpenAI embeddings"

    def handle(self, *args, **kwargs):
        # ✅ Verificar API key
        if not os.environ.get('openai_apikey'):
            self.stderr.write("Error: OpenAI API key not found")
            return

        try:
            # ✅ Seleccionar dos películas para comparar
            movie1 = Movie.objects.get(title="Los juegos del hambre")
            movie2 = Movie.objects.get(title="Matrix")
            
            self.stdout.write(self.style.SUCCESS("🎬 Películas seleccionadas:"))
            self.stdout.write(f"  1. {movie1.title}")
            self.stdout.write(f"  2. {movie2.title}")
            self.stdout.write("")

            # ✅ Obtener embeddings de las películas
            self.stdout.write("🔄 Generando embeddings...")
            emb1 = get_embedding(movie1.description)
            emb2 = get_embedding(movie2.description)

            # ✅ Calcular similitud entre películas
            similarity = cosine_similarity(emb1, emb2)
            self.stdout.write(self.style.SUCCESS("📊 Similitud entre películas:"))
            self.stdout.write(f"  '{movie1.title}' vs '{movie2.title}': {similarity:.4f}")
            self.stdout.write("")

            # ✅ Comparar con un prompt personalizado
            prompt = "película de ciencia ficción distópica con acción y rebelión"
            prompt_emb = get_embedding(prompt)
            
            sim_prompt_movie1 = cosine_similarity(prompt_emb, emb1)
            sim_prompt_movie2 = cosine_similarity(prompt_emb, emb2)

            self.stdout.write(self.style.SUCCESS("🎯 Similitud con el prompt:"))
            self.stdout.write(f"  Prompt: '{prompt}'")
            self.stdout.write(f"  vs '{movie1.title}': {sim_prompt_movie1:.4f}")
            self.stdout.write(f"  vs '{movie2.title}': {sim_prompt_movie2:.4f}")
            self.stdout.write("")

            # ✅ Interpretación de resultados
            self.stdout.write(self.style.SUCCESS("📈 Interpretación:"))
            if similarity > 0.7:
                self.stdout.write("  🟢 Las películas son muy similares")
            elif similarity > 0.4:
                self.stdout.write("  🟡 Las películas tienen similitud moderada")
            else:
                self.stdout.write("  🔴 Las películas son diferentes")

            # ✅ Recomendación basada en el prompt
            self.stdout.write(self.style.SUCCESS("🤖 Recomendación:"))
            if sim_prompt_movie1 > sim_prompt_movie2:
                self.stdout.write(f"  ✅ '{movie1.title}' es más similar al prompt")
            else:
                self.stdout.write(f"  ✅ '{movie2.title}' es más similar al prompt")

        except Movie.DoesNotExist:
            self.stderr.write("Error: No se encontraron las películas especificadas")
            self.stderr.write("Verifica que existan en la base de datos:")
            self.stderr.write("  - Los juegos del hambre")
            self.stderr.write("  - Matrix")
        except Exception as e:
            self.stderr.write(f"Error: {str(e)}")