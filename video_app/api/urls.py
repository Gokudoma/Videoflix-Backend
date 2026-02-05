from django.urls import path
from .views import VideoListView, VideoStreamingView, VideoSegmentView 

urlpatterns = [
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', VideoStreamingView.as_view(), name='video-stream'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', VideoSegmentView.as_view(), name='video-segment'),
]