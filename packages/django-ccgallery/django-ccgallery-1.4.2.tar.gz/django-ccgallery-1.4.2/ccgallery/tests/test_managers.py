from decimal import Decimal
from django.test import TestCase
from ccgallery.models import Item, Category


class ManagerTestCases(TestCase):

    def test_item_for_category(self):
        """the for item manager method"""
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        # make the items
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.status = Item.VISIBLE
        i1.save()
        i1.categories.add(c1)
        i2 = Item()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.status = Item.VISIBLE
        i2.save()
        i2.categories.add(c1)
        # visible returns 1
        self.assertEqual(2, Item.objects.for_category(c1).count())
        # hidden returns 1
        i2.status = Item.HIDDEN
        i2.save()
        self.assertEqual(1, Item.objects.for_category(c1).count())
        # make the category invisible
        c1.status = Category.HIDDEN
        c1.save()
        self.assertEqual(0, Item.objects.for_category(c1).count())

    def test_category_visible(self):
        """only visible categorys are returned"""
        i1 = Category()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.status = Category.VISIBLE
        i1.save()
        i2 = Category()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.status = Category.VISIBLE
        i2.save()
        # visible returns 1
        self.assertEqual(2, Category.objects.visible().count())
        # hidden returns 1
        i2.status = Category.HIDDEN
        i2.save()
        self.assertEqual(1, Category.objects.visible().count())


    def test_category_hidden(self):
        """only hidden categorys are returned"""
        i1 = Category()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.status = Category.VISIBLE
        i1.save()
        i2 = Category()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.status = Category.VISIBLE
        i2.save()
        # visible returns 1
        self.assertEqual(0, Category.objects.hidden().count())
        # hidden returns 1
        i2.status = Category.HIDDEN
        i2.save()
        self.assertEqual(1, Category.objects.hidden().count())


    def test_item_visible(self):
        """only visible items are returned"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.status = Item.VISIBLE
        i1.save()
        i2 = Item()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.status = Item.VISIBLE
        i2.save()
        # visible returns 1
        self.assertEqual(2, Item.objects.visible().count())
        # hidden returns 1
        i2.status = Item.HIDDEN
        i2.save()
        self.assertEqual(1, Item.objects.visible().count())


    def test_item_hidden(self):
        """only hidden items are returned"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.status = Item.VISIBLE
        i1.save()
        i2 = Item()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.status = Item.VISIBLE
        i2.save()
        # visible returns 1
        self.assertEqual(0, Item.objects.hidden().count())
        # hidden returns 1
        i2.status = Item.HIDDEN
        i2.save()
        self.assertEqual(1, Item.objects.hidden().count())

