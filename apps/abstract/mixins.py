# Django Rest Framework
from rest_framework.response import Response
from rest_framework import status

# Python
import logging
from typing import Any


logger = logging.getLogger(__name__)


class ResponseMixin:
    """ResponseMixin."""


    def get_json_response(
        self,
        data: dict[str, Any],
        key_name: str = 'default',
        paginator: Any = None
    ) -> Response:
        """Return pagination response or not..."""

        if paginator:
            return paginator.get_paginated_response(
                data
            )
        return Response(
            {key_name: data}
        )
    

    def response_with_exception(
        self, 
        key_name: str = 'exception',
        message: str = None
    ) -> Response:
        """Logging excepions and return response."""

        logger.warning(str(message))
        return Response(
            {key_name: 'Some problem happend. \
            Do not panic, we are working on this.'}
        )
    

    def response_with_error(
        self,
        key_name: str = 'error',
        message: str = None,
        status = status.HTTP_404_NOT_FOUND
    ) -> Response:
        """Logging errors and return response."""

        logger.error(str(message))
        return Response(
            status=status,
            data={key_name : message}
        )
    
    
    def response_with_critical(
        self,
        key_name: str = 'CRITICAL ERROR',
        message: str = None,
    ) -> Response:
        """Logging critical errors and return response."""
    
        logger.critical(str(message))
        return Response(
            {key_name: 'Some problem happend. \
            Do not panic, we are working on this.'}
        )
