import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq

from .models import Video
from .tasks import convert_480p, convert_720p, convert_1080p

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver that handles actions after a Video object is saved.
    
    If a new video is created, it enqueues conversion tasks for 
    480p, 720p, and 1080p resolutions using django_rq.
    """
    if created:
        print(f'New video created: {instance.id}')
        queue = django_rq.get_queue('default', autocommit=True)
        
        queue.enqueue(convert_480p, instance.video_file.path)
        queue.enqueue(convert_720p, instance.video_file.path)
        queue.enqueue(convert_1080p, instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal receiver that handles actions after a Video object is deleted.
    
    It deletes the associated video file from the filesystem.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print(f'File deleted: {instance.video_file.path}')