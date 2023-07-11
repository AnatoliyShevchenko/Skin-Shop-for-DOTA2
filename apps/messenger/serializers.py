# Rest Framework
from rest_framework.serializers import ModelSerializer, SerializerMethodField

# Local 
from .models import Messages, ChatRoom
from auths.models import Client
from auths.serializers import (
    OneFriendSerializer, 
    UserSerializerForReviews,
)


class ListChatsSerializer(ModelSerializer):
    """Serializer for view chats."""

    members = SerializerMethodField()

    def get_members(self, chatroom):

        members_ids = chatroom.members
        members = Client.objects.filter(id__in=members_ids)
        return OneFriendSerializer(members, many=True).data

    class Meta:
        model = ChatRoom
        fields = (
            'id',
            'title',
            'members',
            'created_at'
        )


class MessageListSerializer(ModelSerializer):
    """Serializer for messages."""

    sender = UserSerializerForReviews()

    class Meta:
        model = Messages
        fields = (
            'id',
            'sender',
            'content',
            'created_at'
        )