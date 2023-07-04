# Django
from django.test import TestCase

# Local
from .models import SkinsBasket, BasketItem, Client, Skins


class SkinsBasketModelTestCase(TestCase):
    """Test for basket."""

    def setUp(self):
        self.client = Client.objects.create(
            username='testuser', 
            email='test@example.com',
            password='testpassword'
        )
        self.skin = Skins.objects.create(name='Skin 1', price=100)
        self.basket = SkinsBasket.objects.create(user=self.client)


    def test_basket_creation(self):
        self.assertIsInstance(self.basket, SkinsBasket)
        self.assertEqual(self.basket.user, self.client)
        self.assertEqual(self.basket.total_price, 0)


    def test_basket_items(self):
        item = BasketItem.objects.create(
            basket=self.basket, 
            skin=self.skin, 
            quantity=2, 
            price=200
        )
        self.assertIn(item, self.basket.basket_items.all())
        self.assertIn(self.skin, self.basket.items.all())
        self.assertEqual(item.totalPrice, item.quantity * item.price)
        self.assertEqual(self.basket.total_price, item.totalPrice)


    def test_basket_item_deletion(self):
        item = BasketItem.objects.create(
            basket=self.basket, 
            skin=self.skin, 
            quantity=2, 
            price=200
        )
        item.delete()
        self.assertNotIn(item, self.basket.basket_items.all())
        self.assertNotIn(self.skin, self.basket.items.all())
        self.assertEqual(self.basket.total_price, 0)

