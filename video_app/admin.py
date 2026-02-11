from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Video model.
    """
    list_display = ('id', 'title', 'created_at')

    def get_form(self, request, obj=None, **kwargs):
        """
        Customizes the form to ensure video_file is mandatory and cannot be cleared.
        """
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['video_file'].required = True
        return form