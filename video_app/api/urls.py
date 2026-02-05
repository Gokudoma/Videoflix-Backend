from django.urls import path
from .views import VideoListView, VideoStreamingView

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoStreamingView.as_view(), name='video-stream'), 
]