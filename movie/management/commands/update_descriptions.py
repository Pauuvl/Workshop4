import os
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv

# ✅ Cargar variables de entorno desde el archivo .env
load_dotenv('openAI.env')

# ✅ Inicializar el cliente de OpenAI con la API Key
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def get_completion(prompt, model="gpt-3.5-turbo"):
    """
    ✅ Función auxiliar para obtener la respuesta de la API
    """
    # Define el mensaje con el rol 'user' y el contenido que enviamos
    messages = [{"role": "user", "content": prompt}]
    
    # Llama a la API con el modelo y los mensajes
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0  # Controla la creatividad (0 = más preciso)
    )
    
    # Retorna solo el contenido de la respuesta generada
    return response.choices[0].message.content.strip()

class Command(BaseCommand):
    help = "Update movie descriptions using OpenAI API (first movie only)"

    def handle(self, *args, **kwargs):
        # ✅ Verificar si la API key está disponible
        if not os.environ.get('openai_apikey'):
            self.stderr.write("Error: OpenAI API key not found in environment variables")
            self.stderr.write("Please check your openAI.env file")
            return

        instruction = "Mejora la descripción de esta película haciéndola más atractiva, detallada y cinematográfica. Hazla más emocionante y engaging para el público:"
        
        # ✅ Obtener todas las películas de la base de datos
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")
        
        # ✅ Recorrer las películas (solo primera por el break)
        for movie in movies:
            try:
                self.stdout.write(f"🔄 Processing: {movie.title}")
                
                # ✅ Construir el prompt específico para Los juegos del hambre
                prompt = f"{instruction} Actualiza la descripción de la película 'Los juegos del hambre'. "
                prompt += "Debe ser una distopía emocionante donde Katniss Everdeen se convierte en el símbolo de la rebelión."
                
                # ✅ Obtener la nueva descripción de la API
                response = get_completion(prompt)
                
                # ✅ Actualizar la descripción en la base de datos
                movie.description = response
                movie.save()
                
                self.stdout.write(self.style.SUCCESS(f"✅ Updated description for: {movie.title}"))
                self.stdout.write(self.style.SUCCESS("📝 New description:"))
                self.stdout.write(self.style.SUCCESS(response[:200] + "..."))  # Muestra solo los primeros 200 caracteres
                
                # ⚠️ BREAK IMPORTANTE - No quitar para ahorrar costos
                self.stdout.write(self.style.WARNING("⏹️ Stopping after first movie (break enabled)"))
                break
                
            except Exception as e:
                self.stderr.write(f"❌ Error processing {movie.title}: {str(e)}")
                break

        self.stdout.write(self.style.SUCCESS("🎉 Finished processing! Only 'Los juegos del hambre' was updated."))