from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Video
from .serializers import VideoSerializer

class VideoListView(generics.ListAPIView):
    """
    API endpoint that returns a list of all videos.
    Requires JWT authentication.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated] # Ensures 401 if not logged in