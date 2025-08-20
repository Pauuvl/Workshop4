from django.db import models

class News(models.Model):
    headline = models.CharField(max_length=200)   # título de la noticia
    body = models.TextField()                     # contenido
    date = models.DateField()                     # fecha de publicación

    def __str__(self):
        return self.headline
