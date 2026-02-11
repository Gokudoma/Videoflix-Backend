import os
import subprocess
from django.core.files import File
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq

from .models import Video
from .tasks import convert_480p, convert_720p, convert_1080p

@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal receiver that handles actions after a Video object is saved.
    
    If a new video is created, it enqueues conversion tasks.
    If the video has no thumbnail, it generates one automatically from the first second.
    """
    if created:
        print(f'New video created: {instance.id}')
        queue = django_rq.get_queue('default', autocommit=True)
        
        queue.enqueue(convert_480p, instance.video_file.path)
        queue.enqueue(convert_720p, instance.video_file.path)
        queue.enqueue(convert_1080p, instance.video_file.path)

    if not instance.thumbnail and instance.video_file:
        video_path = instance.video_file.path
        base, _ = os.path.splitext(video_path)
        temp_thumb_path = f"{base}_temp_thumb.jpg"

        cmd = [
            'ffmpeg', '-i', video_path, '-ss', '00:00:01.000', 
            '-vframes', '1', temp_thumb_path, '-y'
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            if os.path.exists(temp_thumb_path):
                with open(temp_thumb_path, 'rb') as f:
                    filename = f"{os.path.basename(base)}_thumbnail.jpg"
                    instance.thumbnail.save(filename, File(f), save=False)
                
                instance.save(update_fields=['thumbnail'])
                os.remove(temp_thumb_path)
        except subprocess.CalledProcessError:
            print(f"Failed to generate thumbnail for {video_path}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal receiver that handles actions after a Video object is deleted.
    
    It deletes the associated video and thumbnail files from the filesystem.
    """
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
            print(f'File deleted: {instance.video_file.path}')
            
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
            print(f'Thumbnail deleted: {instance.thumbnail.path}')