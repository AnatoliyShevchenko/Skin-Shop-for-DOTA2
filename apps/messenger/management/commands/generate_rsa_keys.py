# Django
from django.core.management.base import BaseCommand
from django.conf import settings

# Third-Party
import rsa


class Command(BaseCommand):
    """Command for generate keys."""

    def generate_keys(self):
        """Generate RSA keys."""

        (public_key, private_key) = rsa.newkeys(2048)

        private_key_str = private_key.save_pkcs1().decode('utf-8')
        public_key_str = public_key.save_pkcs1().decode('utf-8')

        with open(settings.PUBLIC_PATH, 'a') as public:
            public.write(public_key_str)
            public.close()
        
        with open(settings.PRIVATE_PATH, 'a') as private:
            private.write(private_key_str)
            private.close()
            
        print('Keys created.')

    def handle(self, *args, **options):
        self.generate_keys()
        print('GENERATE KEYS SUCCESS.')