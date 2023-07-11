# Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

# SimpleJWT
from rest_framework_simplejwt.authentication import JWTAuthentication

# Django
from django.shortcuts import get_object_or_404

# Local
from abstract.mixins import ResponseMixin
from abstract.paginators import AbstractPaginator
from .models import ChatRoom, Messages
from .serializers import (
    ListChatsSerializer, 
    MessageListSerializer,
)
from auths.models import Client


@permission_classes([IsAuthenticated])
class ChatsViewSet(ResponseMixin, ViewSet):
    """ViewSet for messages."""

    queryset = ChatRoom.objects.all()
    paginator_class = AbstractPaginator()
    authentication_classes = [JWTAuthentication]

    def list(self, request: Request) -> Response:
        """GET method for view all chats."""

        user = request.user
        chats = self.queryset.filter(members__contains=[user.id])
        if chats.exists():
            paginator = self.paginator_class
            objects = paginator.paginate_queryset(
                chats, 
                request=request
            )
            serializer = ListChatsSerializer(
                objects, 
                many=True
            )
            return self.get_json_response(
                key_name='chats',
                data=serializer.data,
                paginator=paginator,
                status='200'
            )
        
        return self.get_json_response(
            key_name='error',
            data='You have no chats at this moment',
            status='200'
        )
    
    def retrieve(self, request: Request, pk: str) -> Response:
        """GET method for view one chat."""

        chat = get_object_or_404(self.queryset, id=pk)
        messages = Messages.objects.filter(chat=chat).order_by('-created_at')

        decrypted_messages = []
        for message in messages:
            decrypted_content = Messages.objects.decrypt_message(message.content)
            decrypted_message = {
                'id': message.id,
                'sender': message.sender,
                'content': decrypted_content,
                'created_at': message.created_at,
            }
            decrypted_messages.append(decrypted_message)

        serializer = MessageListSerializer(decrypted_messages, many=True)

        return self.get_json_response(
            key_name='chat',
            data=serializer.data,
            status='200'
        )

    def create(self, request: Request) -> Response:
        """POST Method for create chats and start messaging."""

        user = request.user
        recipient = request.data.get('recipient')
        content = request.data.get('content')
        try:
            client = Client.objects.get(username=recipient)
            chat_title = f'{user.username},{client.username}'
            chat, created = self.queryset.get_or_create(
                title=chat_title,
                members=[f'{user.id}', client.id]
            )
            Messages.objects.send_message(
                sender=client,
                chat=chat,
                content=content
            )
            return self.get_json_response(
                key_name='chat',
                data='sended',
                status='200'
            )
        except Client.DoesNotExist:
            return self.response_with_exception(
                message=f"""user with username 
                {recipient} does not exist"""
            )