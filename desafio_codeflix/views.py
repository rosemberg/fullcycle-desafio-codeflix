from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import CastMember, Category, Genre, Video, AudioVideoMedia, MediaStatus
from .serializers import (
    CastMemberSerializer, CategorySerializer, GenreSerializer, 
    VideoSerializer, CreateVideoSerializer, UploadVideoMediaSerializer
)
from .base import BaseViewSet

# Create your views here.
class CastMemberViewSet(BaseViewSet):
    """
    API endpoint that allows cast members to be viewed or edited.
    """
    queryset = CastMember.objects.all()
    serializer_class = CastMemberSerializer

class CategoryViewSet(BaseViewSet):
    """
    API endpoint that allows categories to be viewed or edited.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class GenreViewSet(BaseViewSet):
    """
    API endpoint that allows genres to be viewed or edited.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

class VideoViewSet(BaseViewSet):
    """
    API endpoint that allows videos to be viewed or edited.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateVideoSerializer
        elif self.action == 'upload_media':
            return UploadVideoMediaSerializer
        return self.serializer_class

    def create(self, request, *args, **kwargs):
        """
        Create a new video without media.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save()

        # Return only the ID of the created video
        return Response({'id': str(video.id)}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='upload-media', url_name='upload-media')
    def upload_media(self, request, pk=None):
        """
        Upload media for a video.
        """
        video = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'video_id': pk})
        serializer.is_valid(raise_exception=True)
        media = serializer.save()

        return Response({'id': str(media.id)}, status=status.HTTP_201_CREATED)
