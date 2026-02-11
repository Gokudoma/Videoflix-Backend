from django.db import models
from django.utils import timezone

class Video(models.Model):
    """
    Model representing a video entity with its metadata and associated source files.
    """
    CATEGORY_CHOICES = [
        ('drama', 'Drama'),
        ('documentary', 'Documentary'),
        ('romance', 'Romance'),
        ('comedy', 'Comedy'),
    ]

    title = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    video_file = models.FileField(upload_to='videos')
    thumbnail = models.FileField(upload_to='thumbnails', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='drama')

    def __str__(self):
        return self.title