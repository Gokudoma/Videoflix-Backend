from django.db import models
from django.utils import timezone

class Video(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField(max_length=500)
    created_at = models.DateTimeField(default=timezone.now)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    thumbnail = models.FileField(upload_to='thumbnails', blank=True, null=True)

    def __str__(self):
        return self.title