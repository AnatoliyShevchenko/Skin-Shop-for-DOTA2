# Django
from django.test import TestCase

# Local
from .models import Client, Invites


class TestClientModel(TestCase):
    """Test for Client model."""

    def setUp(self) -> None:
        self.user = Client.objects.create_user(
            email='test@email.com',
            username='Username',
            password='qtreg4w4t33__124'
        )

    
    def test_user_creation(self):
        self.assertEqual(self.user.email, 'test@email.com')
        self.assertEqual(self.user.usename, 'Username')
        self.assertEqual(self.user.password, 'qtreg4w4t33__124')
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.is_superuser)


    def test_superuser_creation(self):
        superuser = Client.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpassword'
        )
        self.assertEqual(superuser.email, 'admin@example.com')
        self.assertEqual(superuser.username, 'admin')
        self.assertTrue(superuser.is_active)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


    def test_save_method(self):
        self.user.first_name = 'Simple'
        self.user.last_name = 'Example'
        self.user.save()
        saved_user = Client.objects.get(pk=self.user.pk)
        self.assertEqual(saved_user.first_name, 'Simple')
        self.assertEqual(saved_user.last_name, 'Example')


    def test_friends_field(self):
        self.user.friends.append(1)
        self.user.friends.append(2)
        self.user.friends.append(3)
        self.user.save()
        saved_user = Client.objects.get(pk=self.user.pk)
        self.assertEqual(saved_user.friends, [1, 2, 3])


class TestInvites(TestCase):
    """Test for invites."""


    def setUp(self) -> None:
        self.from_user = Client.objects.create_user(
            email='from@example.com',
            username='fromuser',
            password='frompassword',
        )
        self.to_user = Client.objects.create_user(
            email='to@example.com',
            username='touser',
            password='topassword',
        )
        self.invite = Invites.objects.create(
            from_user=self.from_user,
            to_user=self.to_user
        )


    def test_accept_invite(self):
        Invites.objects.accept_invite(self.invite)
        self.invite.refresh_from_db()
        self.assertTrue(self.invite.status)
        self.assertEqual(self.from_user.friends, [self.to_user.id])
        self.assertEqual(self.to_user.friends, [self.from_user.id])


    def test_reject_invite(self):
        Invites.objects.reject_invite(self.invite)
        self.invite.refresh_from_db()
        self.assertFalse(self.invite.status)


    def test_invites_model(self):
        self.assertEqual(
            str(self.invite), 
            f'{self.from_user} | \
            {self.to_user} | \
            {self.invite.status}'
        )
        self.assertEqual(self.invite.from_user, self.from_user)
        self.assertEqual(self.invite.to_user, self.to_user)
        self.assertTrue(self.invite.date_created)

        duplicate_invite = Invites(
            from_user=self.from_user,
            to_user=self.to_user
        )
        with self.assertRaises(Exception):
            duplicate_invite.full_clean()

        self.invite.status = None
        self.invite.save()
        self.assertIsNone(self.invite.status)

        self.invite.status = True
        self.invite.save()
        self.assertTrue(self.invite.status)

        self.invite.status = False
        self.invite.save()
        self.assertFalse(self.invite.status)

        