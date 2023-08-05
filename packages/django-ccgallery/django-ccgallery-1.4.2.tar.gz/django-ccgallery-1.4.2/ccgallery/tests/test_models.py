import os
from decimal import Decimal
from unittest import skipUnless
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from ccgallery.models import Item, Category, ItemImage


red = os.path.exists('%s/ccgallery/red.jpg' % settings.STATIC_ROOT)
blue = os.path.exists('%s/ccgallery/blue.jpg' % settings.STATIC_ROOT)

class CategoryTestCases(TestCase):

    @skipUnless(red, 'red.png file does not exist')
    @skipUnless(blue, 'blue.png file does not exist')
    def test_category_images(self):
        """ A category will return the first image from the first 
        available item in it's set"""
        # the images
        red = open('%s/ccgallery/red.jpg' % settings.STATIC_ROOT)
        blue = open('%s/ccgallery/blue.jpg' % settings.STATIC_ROOT)
        # make items
        i1 = Item()
        i1.status = Item.VISIBLE
        i1.name = '1'
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i2 = Item()
        i2.status = Item.VISIBLE
        i2.name = '2'
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.save()
        # make the images
        ii1 = ItemImage()
        ii1.item = i1
        ii1.src = File(red, 'ccgallery/red.jpg')
        ii1.order = Decimal('10.00')
        ii1.save()
        ii2 = ItemImage()
        ii2.item = i2
        ii2.src = File(blue, 'ccgallery/blue.jpg')
        ii2.save()
        # make category
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        # add images to the categories
        i1.categories.add(c1)
        i2.categories.add(c1)
        # close the images
        red.close()
        blue.close()
        # now the category image is ii2
        self.assertEqual(c1.image.pk, ii2.pk)
        # make i2 hidden
        i2.status = Item.HIDDEN
        i2.save()
        # now the category image is ii1
        self.assertEqual(c1.image.pk, ii1.pk)
        # make i1 hidden and now it's none
        i1.status = Item.HIDDEN
        i1.save()
        # now the category image is ii1
        self.assertEqual(c1.image, None)


class ItemTestCases(TestCase):

    def test_ordering(self):
        """items are ordered by their order"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i2 = Item()
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.save()
        i3 = Item()
        i3.slug = '3'
        i3.title = '3'
        i3.description = '3'
        i3.order = Decimal('1.00')
        i3.save()
        # 3 is first, 2 second and 1 third
        self.assertEqual('3', Item.objects.all()[0].slug)
        self.assertEqual('2', Item.objects.all()[1].slug)
        self.assertEqual('1', Item.objects.all()[2].slug)


    def test_created(self):
        """items have a created date added when they're created"""
        i = Item()
        i.slug = '1'
        i.title = '1'
        i.description = '1'
        i.save()
        self.assertTrue(i.created)

    def test_url(self):
        """items return their url correctly"""
        i = Item()
        i.slug = '1'
        i.title = '1'
        i.description = '1'
        i.save()
        self.assertTrue(len(i.get_absolute_url()) > 0)
