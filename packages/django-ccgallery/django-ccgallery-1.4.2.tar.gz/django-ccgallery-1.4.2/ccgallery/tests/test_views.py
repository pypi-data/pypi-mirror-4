from django.test import TestCase
from django.core.urlresolvers import reverse
from ccgallery.tests.mockrequest import MockRequest
from ccgallery.models import Item, Category
from ccgallery.views import index, item, category

class ViewTestCases(TestCase):

    def setUp(self):
        self.rf = MockRequest()

    def test_category_404(self):
        """if a category doesn't exist a 404 is raised"""
        r = self.client.get(reverse('ccgallery:category', args=['1']))
        self.assertEqual(404, r.status_code)
    
    def test_item_404(self):
        """if a item doesn't exist a 404 is raised"""
        r = self.client.get(reverse('ccgallery:item', args=['1']))
        self.assertEqual(404, r.status_code)

    def test_index_200(self):
        """index responds with a 200 OK"""
        request = self.rf.get(reverse('ccgallery:index'))
        response  = index(request)
        # is 200
        self.assertEqual(200, response.status_code)

    def test_item_200(self):
        """item responds with a 200 OK"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        request = self.rf.get(reverse('ccgallery:item', args=[i1.slug]))
        response  = item(request, i1.slug)
        # is 200
        self.assertEqual(200, response.status_code)

    def test_item_200_with_category(self):
        """item responds with a 200 OK"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        i1.categories.add(c1)
        request = self.rf.get(
                reverse('ccgallery:item', args=[c1.slug, i1.slug]))
        response  = item(request, i1.slug, c1.slug)
        # is 200
        self.assertEqual(200, response.status_code)

    def test_item_200_with_fake_category(self):
        """item responds with a 200 OK"""
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        request = self.rf.get(
                reverse('ccgallery:item', args=['horse', i1.slug]))
        response  = item(request, i1.slug, 'horse')
        # is 200
        self.assertEqual(200, response.status_code)
    def test_category_200(self):
        """category responds with a 200 OK"""
        c1 = Category()
        c1.slug = '1'
        c1.title = '1'
        c1.description = '1'
        c1.status = Category.VISIBLE
        c1.save()
        i1 = Item()
        i1.slug = '1'
        i1.title = '1'
        i1.description = '1'
        i1.save()
        i1.categories.add(c1)
        request = self.rf.get(
                reverse('ccgallery:category', args=[c1.slug]))
        response = category(request, c1.slug)
        # is 200
        self.assertEqual(200, response.status_code)
