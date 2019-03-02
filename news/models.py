from django.db import models


class Post(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.CharField(max_length=200)
    uri = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title
