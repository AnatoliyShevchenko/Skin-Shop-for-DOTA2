# Django
from django.core.management.base import BaseCommand
from django.conf import settings

# Third-Party
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Python
from typing import Any
import os


ENV = os.path.join(settings.BASE_DIR, '.env')


class Command(BaseCommand):
    """Command for generate keys."""

    def generate_keys(self):
        """Generate RSA keys."""

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        public_key = private_key.public_key()

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        PRIVATE_KEY = private_key_pem.decode('utf-8')
        PUBLIC_KEY = public_key_pem.decode('utf-8')

        with open(ENV, 'a') as keys:
            keys.write('\n')
            keys.write('# RSA \n')
            keys.write(f'PRIVATE_KEY={PRIVATE_KEY}\n')
            keys.write(f'PUBLIC_KEY={PUBLIC_KEY}\n')

        print('Keys created.')

    
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.generate_keys()
        print('GENERATE KEYS SUCCESS.')