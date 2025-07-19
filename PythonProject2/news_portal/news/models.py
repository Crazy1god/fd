from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.CharField(max_length=100)
    published_date = models.DateTimeField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return self.title