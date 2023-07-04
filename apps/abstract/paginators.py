# Django Rest Framework
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.serializer_helpers import ReturnList


class AbstractPaginator(PageNumberPagination):
    """Paginator maybe for all."""

    page_size_query_param: str = 'size'
    page_query_param: str = 'page'
    max_page_size: int = 50
    page_size: int = 25

    def get_paginated_response(
        self,
        data: ReturnList,
        status
    ) -> Response:

        response: Response = \
            Response(
                {
                    'pagination': {
                        'next': self.get_next_link(),
                        'previous': self.get_previous_link(),
                        'count': self.page.paginator.num_pages
                    },
                    'items': data,
                },
                status=status
            )
        return response

