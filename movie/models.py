from django.db import models
import numpy as np

def get_default_array():
    """Función para crear un array por defecto (ceros)"""
    default_arr = np.zeros(1536, dtype=np.float32)  # text-embedding-3-small tiene 1536 dimensiones
    return default_arr.tobytes()

class Movie(models.Model): 
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1500) 
    image = models.ImageField(upload_to='movie/images/', default='movie/images/default.jpg') 
    url = models.URLField(blank=True)
    genre = models.CharField(blank=True, max_length=250)
    year = models.IntegerField(blank=True, null=True)
    emb = models.BinaryField(default=get_default_array())  # ✅ Nuevo campo para embeddings

    def __str__(self): 
        return self.title
    
    def get_embedding_array(self):
        """Convierte el campo binario de vuelta a array numpy"""
        return np.frombuffer(self.emb, dtype=np.float32)