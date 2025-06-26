from rest_framework.response import Response
from rest_framework import status
from .models import CastMember, Category, Genre, Video
from .serializers import (
    CastMemberSerializer, CategorySerializer, GenreSerializer, 
    VideoSerializer, CreateVideoSerializer
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
