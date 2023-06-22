# Django
from django.test import TestCase
from django.core.exceptions import ValidationError

# Local
from .models import Skins, Client, UserSkins, Reviews


class SkinsModelTestCase(TestCase):
    """Test for Skins."""


    def setUp(self):
        self.skin = Skins.objects.create(
            title='Skin 1',
            name='Skin Name',
            grade='Grade A',
            rating=4,
            category=1,
            priceWithoutSale=1000,
            sale=20,
            realPrice=800
        )


    def test_skin_creation(self):
        self.assertIsInstance(self.skin, Skins)
        self.assertEqual(self.skin.title, 'Skin 1')
        self.assertEqual(self.skin.name, 'Skin Name')
        self.assertEqual(self.skin.grade, 'Grade A')
        self.assertEqual(self.skin.rating, 4)
        self.assertEqual(self.skin.category, 1)
        self.assertEqual(self.skin.priceWithoutSale, 1000)
        self.assertEqual(self.skin.sale, 20)
        self.assertEqual(self.skin.realPrice, 800)


    def test_changed_fields(self):
        self.assertEqual(self.skin.changed_fields(), {})

        self.skin.title = 'New Title'
        self.skin.save()

        changed_fields = self.skin.changed_fields()
        self.assertIn('title', changed_fields)
        self.assertEqual(changed_fields['title'], 'New Title')


    def test_string_representation(self):
        self.assertEqual(str(self.skin), 'Skin 1')


class UserSkinsModelTestCase(TestCase):
    """Tests fot UsersSkins."""

    def setUp(self):
        self.client = Client.objects.create(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            cash=1000
        )
        self.skin = Skins.objects.create(
            title='Skin 1',
            name='Skin Name',
            grade='Grade A',
            rating=4,
            category=1,
            priceWithoutSale=1000,
            sale=20,
            realPrice=800
        )
        self.user_skins = UserSkins.objects.create(
            user=self.client,
            skin=self.skin,
            quantity=3
        )


    def test_user_skins_creation(self):
        self.assertIsInstance(self.user_skins, UserSkins)
        self.assertEqual(self.user_skins.user, self.client)
        self.assertEqual(self.user_skins.skin, self.skin)
        self.assertEqual(self.user_skins.quantity, 3)


    def test_string_representation(self):
        self.assertEqual(str(self.user_skins), 'testuser')


    def test_skin_quantity_validator(self):
        with self.assertRaises(ValidationError):
            self.user_skins.quantity = 0
            self.user_skins.full_clean()


    def test_skin_quantity_default_value(self):
        user_skins = UserSkins.objects.create(
            user=self.client, 
            skin=self.skin
        )
        self.assertEqual(user_skins.quantity, 1)


class ReviewsModelTest(TestCase):
    """Tests for reviews."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client.objects.create(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        cls.skin = Skins.objects.create(
            title='Skin 1',
            name='Skin Name',
            grade='Grade A',
            rating=4,
            category=1,
            priceWithoutSale=1000,
            sale=20,
            realPrice=800
        )


    def test_create_review(self):
        review = Reviews.objects.create(
            user=self.client,
            skin=self.skin,
            review='This is a test review',
            rating=4
        )
        self.assertEqual(review.user, self.client)
        self.assertEqual(review.skin, self.skin)
        self.assertEqual(review.review, 'This is a test review')
        self.assertEqual(review.rating, 4)


    def test_review_rating_validation(self):
        with self.assertRaises(ValidationError):
            Reviews.objects.create(
                user=self.client,
                skin=self.skin,
                review='This is a test review',
                rating=6
            )