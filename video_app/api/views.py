# 1. Standard Library Imports
import os

# 2. Third-Party Library Imports (Django & REST Framework)
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# 3. Local Application Imports
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
    
    
class VideoSegmentView(views.APIView):
    """
    API endpoint to serve HLS video segments (.ts files).
    
    Example URL: /api/video/1/480p/segment001.ts
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        video = get_object_or_404(Video, pk=movie_id)
        
        # The segments are located in the same directory as the original video file
        video_directory = os.path.dirname(video.video_file.path)
        
        # Construct the full path to the requested segment
        segment_path = os.path.join(video_directory, segment)

        if not os.path.exists(segment_path):
            raise Http404("Segment not found.")

        # Return the binary segment file with the correct content type
        return FileResponse(open(segment_path, 'rb'), content_type='video/MP2T')    