from rest_framework import viewsets, serializers
from rest_framework.response import Response
from .pagination import CustomPagination

class BaseSerializer(serializers.ModelSerializer):
    """
    Base serializer with common functionality for all domain serializers.
    """
    pass

class BaseViewSet(viewsets.ModelViewSet):
    """
    Base viewset with common functionality for all domain viewsets.
    """
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})