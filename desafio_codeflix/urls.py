from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CastMemberViewSet

router = DefaultRouter()
router.register(r'cast_members', CastMemberViewSet, basename='castmember')

urlpatterns = [
    path('', include(router.urls)),
]
