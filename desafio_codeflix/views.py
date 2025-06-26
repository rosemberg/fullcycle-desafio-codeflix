from .models import CastMember
from .serializers import CastMemberSerializer
from .base import BaseViewSet

# Create your views here.
class CastMemberViewSet(BaseViewSet):
    """
    API endpoint that allows cast members to be viewed or edited.
    """
    queryset = CastMember.objects.all()
    serializer_class = CastMemberSerializer
