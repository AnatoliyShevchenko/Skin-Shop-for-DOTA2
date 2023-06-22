# # Django Rest Framework
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.viewsets import ViewSet
# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAuthenticated

# # SimpleJWT
# from rest_framework_simplejwt.authentication import JWTAuthentication

# # Local
# from .models import Messages
# from auths.models import Client
# from .serializers import (
#     CreateMessageSerializer, 
#     MessageListSerializer,
# )
# from abstract.mixins import ResponseMixin
# from abstract.paginators import AbstractPaginator
# from abstract.validators import APIValidator

# # Python
# from datetime import datetime


# @permission_classes([IsAuthenticated])
# class MessagesViewSet(ResponseMixin, ViewSet):
#     """ViewSet for messages."""

#     queryset = Messages.objects
#     paginator_class = AbstractPaginator()
#     authentication_classes = [JWTAuthentication]


#     def list(self, request: Request) -> Response:
#         """GET Method, not implemented in this view."""

#         raise APIValidator(
#             'метод list не имплементирован',
#             'warning',
#             '202'
#         )
    

#     def retrieve(self, request: Request, pk: str) -> Response:
#         """View messages with concrete user."""

#         user = request.user
#         try:
#             friend = Client.objects.get(id=pk)
#             messages = self.queryset.get_old_messages(
#                 sender=friend,
#                 recipient=user,
#                 offset=datetime.now()
#             )
#             recieved_messages = Messages.objects.receive_message()
#             messages += recieved_messages
#             serializer = MessageListSerializer(
#                 messages,
#                 many=True
#             )
#             return self.get_json_response(
#                 key_name='messages',
#                 data=serializer.data
#             )
#         except Client.DoesNotExist:
#             return self.get_json_response(
#                 key_name='error',
#                 data='user not found'
#             )
    

#     def create(self, request: Request) -> Response:
#         """Create message."""

#         user = request.user
#         recipient = request.data.get('recipient')
#         try:
#             friend = Client.objects.get(username=recipient)
#             serializer = CreateMessageSerializer(data=request.data)
#             serializer.is_valid(raise_exception=True)
#             content = serializer.validated_data.get('content')
#             self.queryset.send_message(
#                 sender=user,
#                 recipient=friend,
#                 content=content
#             )
#             return self.get_json_response(
#                 key_name='message',
#                 data='message created'
#             )
#         except Client.DoesNotExist:
#             return self.response_with_error(
#                 message='user not found'
#             )
        