from rest_framework import viewsets
from rest_framework.response import Response
from .models import CastMember
from .serializers import CastMemberSerializer

# Create your views here.
class CastMemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cast members to be viewed or edited.
    """
    queryset = CastMember.objects.all()
    serializer_class = CastMemberSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})
