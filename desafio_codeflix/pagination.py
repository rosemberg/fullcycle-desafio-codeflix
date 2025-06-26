from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_query_param = 'current_page'
    page_size = 10  # Default page size
    
    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'current_page': self.page.number,
                'per_page': self.page_size,
                'total': self.page.paginator.count
            }
        })