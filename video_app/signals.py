"""
Signals for the video_app.
Handles post-save and post-delete events to manage video files and tasks.
"""
import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import Video

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Triggered when a Video object is saved.
    Can be used to start encoding tasks or logging.
    """
    if created:
        print(f'New video created: {instance.id}')
        # Example: Add to conversion queue
        # queue = django_rq.get_queue('default', autocommit=True)
        # queue.enqueue(convert_480p, instance.video_file.path)


#@receiver(post_delete, sender=Video)
#def video_post_delete(sender, instance, **kwargs):
#  """
#  Triggered when a Video object is deleted.
#  Deletes the actual file from the filesystem to clean up.
#   """
#if instance.video_file:
#    if os.path.isfile(instance.video_file.path):
#       os.remove(instance.video_file.path)
#    print(f'File deleted: {instance.video_file.path}')