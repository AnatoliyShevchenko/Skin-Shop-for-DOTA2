# # Django
# from django.db import models
# from django.db.models import Q

# # Local
# from auths.models import Client

# # Third-Party
# from cryptography.hazmat.primitives import (
#     serialization, 
#     hashes,
# )
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.backends import default_backend
# from base64 import (
#     b64encode, 
#     b64decode,
# )
# from decouple import config
# import pika


# PRIVATE_KEY_STR = config('PRIVATE_KEY')
# PUBLIC_KEY_STR = config('PUBLIC_KEY')


# class MessageManager(models.Manager):
#     """Manager for messages."""


#     def connect_rabbit(self, message):
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host='my-rabbitmq')
#         )
#         channel = connection.channel()
#         channel.queue_declare(queue='messages')
#         channel.basic_publish(
#             exchange='',
#             routing_key='messages',
#             body=message,
#         )
#         connection.close()
#         return message


#     def encrypt_message(self, message):
#         public_key = serialization.load_pem_public_key(
#             data=PUBLIC_KEY_STR.encode(),
#             backend=default_backend()
#         )
#         encrypted_message = public_key.encrypt(
#             message.encode(),
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )

#         encoded_message = b64encode(encrypted_message).decode('utf-8')

#         return encoded_message


#     def decrypt_message(self, message):
#         private_key = serialization.load_pem_private_key(
#             data=PRIVATE_KEY_STR.encode(),
#             password=None,
#             backend=default_backend()
#         )
#         encrypted_message = b64decode(message.encode())

#         decrypted_message = private_key.decrypt(
#             encrypted_message,
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )
#         return decrypted_message.decode('utf-8')


#     def send_message(self, sender, recipient, content):
#         message = self.create(
#             sender=sender,
#             recipient=recipient,
#             content=self.encrypt_message(content),
#             sended=True
#         )
#         self.connect_rabbit(message=message.content)
#         return message
    

#     def receive_message(self):
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host='my-rabbitmq')
#         )
#         channel = connection.channel()
#         channel.queue_declare(queue='messages')

#         recieved_messages = []


#         def callback(ch, method, properties, body):
#             recieved_messages.append(body.decode('utf-8'))

#         channel.basic_consume(
#             queue='messages', 
#             on_message_callback=callback, 
#             auto_ack=True
#         )
#         channel.start_consuming()

#         return recieved_messages


#     def get_old_messages(self, sender, recipient, offset):
#         messages = self.filter(
#             Q(sender=sender, recipient=recipient)|\
#             Q(sender=recipient, recipient=sender),
#             created_at__lt=offset
#         ).order_by('-created_at')[:40]

#         decrypted_messages = []
#         for message in messages:
#             decrypted_content = self.decrypt_message(
#                 message=message.content
#             )
#             decrypted_message = {
#                 'id' : message.id,
#                 'sender' : message.sender,
#                 'recipient' : message.recipient,
#                 'content' : decrypted_content,
#                 'created_at' : message.created_at,
#                 'sended' : message.sended,
#                 'delivered' : message.delivered,
#                 'readed' : message.readed
#             }
#             decrypted_messages.append(decrypted_message)
#         return decrypted_messages


# class Messages(models.Model):
#     """Class for chat between users."""

#     sender = models.ForeignKey(
#         to=Client,
#         on_delete=models.CASCADE,
#         related_name='sender_message',
#         verbose_name='отправитель'
#     )
#     recipient = models.ForeignKey(
#         to=Client,
#         on_delete=models.CASCADE,
#         related_name='recipient_message',
#         verbose_name='получатель'
#     )
#     content = models.TextField(
#         verbose_name='сообщение',
#         max_length=500,
#     )
#     created_at = models.DateTimeField(
#         verbose_name='дата создания',
#         auto_now_add=True
#     )
#     sended = models.BooleanField(
#         verbose_name='отправлено',
#         default=False
#     )
#     delivered = models.BooleanField(
#         verbose_name='доставлено',
#         null=True
#     )
#     readed = models.BooleanField(
#         verbose_name='прочитано',
#         default=False
#     )

#     objects = MessageManager()

#     class Meta:
#         ordering = ('created_at',)
#         verbose_name = 'сообщение',
#         verbose_name_plural = 'сообщения'


#     def __str__(self) -> str:
#         return f'{self.sender} to {self.recipient} \
#             at {self.created_at}'
    
