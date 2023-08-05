from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from ccgallery.models import Category, get_model


def category(request, slug):

    try:
        category = Category.objects.visible().get(slug=slug)
    except Category.DoesNotExist:
        raise Http404('Category slug not found')

    items = get_model().objects\
            .visible()\
            .filter(categories=category)

    return render_to_response(
            'ccgallery/category.html', {
                'category': category,
                'items': items,
                }, RequestContext(request))


def item(request, slug, category_slug=None):
    model_cls = get_model()
    category = None

    try:
        item = model_cls.objects.visible().get(slug=slug)
    except model_cls.DoesNotExist:
        raise Http404('Item slug not found')

    if category_slug != None:
        try:
            category = Category.objects.visible().get(
                    slug=category_slug)
        except Category.DoesNotExist:
            pass

    return render_to_response(
            'ccgallery/item.html', {
                'item': item,
                'category': category,
                }, RequestContext(request))


def index(request):
    categories = Category.objects.visible()

    return render_to_response(
            'ccgallery/index.html', {
                'categories': categories,
                }, RequestContext(request))
