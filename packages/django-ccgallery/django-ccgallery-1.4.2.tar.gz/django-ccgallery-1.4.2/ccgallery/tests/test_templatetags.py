import os
from unittest import skipIf
from decimal import Decimal
from django.conf import settings
from django.test import TestCase
from django.core.files import File
from mock import patch
from ccgallery.models import Item, Category
from ccgallery.templatetags import ccgallery_tags

# we need mock for these tests
try:
    import mock
    skip_templatetagtestcases = False
except ImportError:
    skip_templatetagtestcases = True
# we need the test files
red = os.path.exists('%s/ccstraps/red.png' % settings.STATIC_ROOT)
purple = os.path.exists('%s/ccstraps/purple.png' % settings.STATIC_ROOT)

# the mock context
class ContextMock(dict):
    autoescape = object()


@skipIf(skip_templatetagtestcases, 'mock library required')
class TemplatetagTestCases(TestCase):

    @patch('django.template.loader.get_template')
    @patch('django.template.Context')
    def test_get_item_no_category(self, get_template, Context):
        """get items with no category works as expected"""
        # make two items
        i1 = Item()
        i1.status = Item.VISIBLE
        i1.name = '1'
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i2 = Item()
        i2.status = Item.HIDDEN
        i2.name = '2'
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.save()
        # get the node
        node = ccgallery_tags.ItemNode('items')
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual(1, context['items'].count())

    @patch('django.template.loader.get_template')
    @patch('django.template.Context')
    def test_get_item_one_category(self, get_template, Context):
        """get items with one category works as expected"""
        # make category
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        # make two items
        i1 = Item()
        i1.status = Item.VISIBLE
        i1.name = '1'
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i1.categories.add(c1)
        i2 = Item()
        i2.status = Item.HIDDEN
        i2.name = '2'
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.save()
        i2.categories.add(c1)
        # get the node
        node = ccgallery_tags.ItemNode('items', c1.pk)
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual(1, context['items'].count())
        # make i2 visible and the count changes
        i2.status = Item.VISIBLE
        i2.save()
        # get the node
        node = ccgallery_tags.ItemNode('items', c1.pk)
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual(2, context['items'].count())


    @patch('django.template.loader.get_template')
    @patch('django.template.Context')
    def test_get_item_category_comma(self, get_template, Context):
        """get items with comma seperated categories work as expected"""
        # make category
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        c2 = Category()
        c2.slug = '1'
        c2.title = '1'
        c2.description = '1'
        c2.status = Category.VISIBLE
        c2.save()
        # make two items
        i1 = Item()
        i1.status = Item.VISIBLE
        i1.name = '1'
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i1.categories.add(c1)
        i2 = Item()
        i2.status = Item.HIDDEN
        i2.name = '2'
        i2.slug = '2'
        i2.title = '2'
        i2.description = '2'
        i2.order = Decimal('2.00')
        i2.save()
        i2.categories.add(c1)
        # get the node
        node = ccgallery_tags.ItemNode('items', '%s,%s' % (c1.pk, c2.pk))
        # now build the context
        context = ContextMock({})
        # now we can render
        node.render(context)
        self.assertEqual(1, context['items'].count())
