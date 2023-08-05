try:
    import textile
except ImportError:
    pass
try:
    import markdown2
except ImportError:
    pass
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from ccgallery import settings as c_settings
from ccgallery.models import get_model

register = template.Library()

class ItemNode(template.Node):

    def __init__(self, varname, categories=None):
        self.varname = varname
        self.categories = categories

    def render(self, context):
        items = get_model().objects\
                .visible()
        if self.categories is not None:
            try:
                categories = self.categories.split(',')
            except AttributeError:
                categories = [self.categories]
            items = items.filter(
                    categories__pk__in=categories)
        context[self.varname] = items
        return ''

@register.tag
def get_items(parser, token):
    bits = token.contents.split()
    try:
        categories = bits[4]
    except IndexError:
        categories = None
    return ItemNode(bits[2], categories)




class RandomItemNode(template.Node):

    def __init__(self, display, varname):
        self.display = display
        self.varname = varname

    def render(self, context):
        items = get_model().objects\
                .visible()\
                .order_by('?')[:self.display]
        context[self.varname] = items
        return ''

@register.tag
def get_gallery_items(parser, token):
    bits = token.contents.split()
    return RandomItemNode(bits[1], bits[3])

@register.inclusion_tag('ccgallery/_js.html')
def gallery_js():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccgallery/_css.html')
def gallery_css():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.filter
def markup(text):
    """output the description according to whatever markup
    language is set in the settings"""
    html = ''
    if c_settings.MARKUP_LANGUAGE == 'textile':
        html = textile.textile(text)

    if c_settings.MARKUP_LANGUAGE == 'markdown':
        html = markdown2.markdown(text)

    return mark_safe(html)
