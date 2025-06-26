from rest_framework import viewsets
from .models import CastMember
from .serializers import CastMemberSerializer

# Create your views here.
class CastMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cast members to be viewed or edited.
    """
    queryset = CastMember.objects.all()
    serializer_class = CastMemberSerializer
