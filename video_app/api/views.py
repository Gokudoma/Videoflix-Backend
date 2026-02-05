import os
from rest_framework import generics, views 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response # Falls noch nicht da
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from ..models import Video
from .serializers import VideoSerializer

class VideoListView(generics.ListAPIView):
    """
    API endpoint that returns a list of all videos.
    Requires JWT authentication.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]


class VideoStreamingView(views.APIView):
    """
    API endpoint to serve HLS master playlist for a specific video and resolution.
    
    Example URL: /api/video/1/480p/index.m3u8
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        video = get_object_or_404(Video, pk=movie_id)
        
        # Construct the file path based on the resolution
        # Example: /media/videos/myvideo_480p.m3u8
        video_path = video.video_file.path
        base, _ = os.path.splitext(video_path)
        playlist_path = f"{base}_{resolution}.m3u8"

        if not os.path.exists(playlist_path):
            raise Http404("Video or manifest not found.")

        # Return the file with the correct MIME type for HLS
        return FileResponse(open(playlist_path, 'rb'), content_type='application/vnd.apple.mpegurl')