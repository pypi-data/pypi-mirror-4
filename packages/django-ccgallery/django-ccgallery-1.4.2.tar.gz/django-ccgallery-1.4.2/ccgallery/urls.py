from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^/(?P<slug>[\w\-]+).html',
        'ccgallery.views.item',
        name='item'),
    url(r'^/(?P<category_slug>[\w\-]+)/(?P<slug>[\w\-]+).html',
        'ccgallery.views.item',
        name='item'),
    url(r'^/(?P<slug>[\w\-]+)/',
        'ccgallery.views.category',
        name='category'),
    url(r'^\.html',
        'ccgallery.views.index',
        name='index'),
)
