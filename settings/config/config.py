# Python
from typing import Any

# Django Rest Framework
from rest_framework import status


STATUS_CODES: dict[str, Any] = {
    '500': status.HTTP_500_INTERNAL_SERVER_ERROR,
    '404': status.HTTP_404_NOT_FOUND,
    '403': status.HTTP_403_FORBIDDEN,
    '400': status.HTTP_400_BAD_REQUEST,
    '202': status.HTTP_202_ACCEPTED,
    '200': status.HTTP_200_OK,
}

VALIDATE_PATTERN = r"""^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%&*_\-])[a-zA-Z0-9!@#$%&*_\-]+$"""


