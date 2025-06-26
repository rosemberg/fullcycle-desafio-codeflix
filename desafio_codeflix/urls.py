from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CastMemberViewSet, CategoryViewSet, GenreViewSet, VideoViewSet

router = DefaultRouter()
router.register(r'cast_members', CastMemberViewSet, basename='castmember')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'genres', GenreViewSet, basename='genre')
router.register(r'videos', VideoViewSet, basename='video')

urlpatterns = [
    path('', include(router.urls)),
]
