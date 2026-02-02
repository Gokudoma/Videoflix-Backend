from rest_framework import serializers
from ..models import Video

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model.
    Maps the 'thumbnail' field to 'thumbnail_url' to match frontend requirements.
    """
    thumbnail_url = serializers.ImageField(source='thumbnail', read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail_url', 'category']