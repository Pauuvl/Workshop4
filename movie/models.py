from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=100, default="Desconocido")  # Nuevo campo
    year = models.IntegerField(null=True, blank=True)                # Nuevo campo
    image = models.ImageField(upload_to='movie/images/', null=True, blank=True)
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.year})"
