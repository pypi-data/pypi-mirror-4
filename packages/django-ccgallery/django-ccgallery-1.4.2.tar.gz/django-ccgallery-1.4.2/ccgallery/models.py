from django.db import models
from ccgallery import import_thing
from ccgallery import listeners
from ccgallery import managers
import ccgallery.settings as c_settings
from ccthumbs.fields import ImageWithThumbsField


def get_model():
    model = Item
    if c_settings.MODEL:
        try:
            module, model = import_thing(c_settings.MODEL)
        except (AttributeError, ImportError):
            pass

    return model


class Category(models.Model):
    HIDDEN = 0
    VISIBLE = 1
    CATEGORY_CHOICES = (
        (HIDDEN, 'Hidden'),
        (VISIBLE, 'Visible'),
    )
    name = models.CharField(
            max_length=255)
    slug = models.SlugField()
    description = models.TextField(
            blank=True,
            null=True)
    order = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default='5.00')
    created = models.DateTimeField(
            blank=True,
            null=True)
    status = models.PositiveSmallIntegerField(
            choices=CATEGORY_CHOICES,
            default=c_settings.CATEGORY_DEFAULT_STATUS)

    objects = managers.CategoryManager()

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('ccgallery:category', (), {
            'slug': self.slug,
            })

    @property
    def image(self):
        """returns the first image from the first visible item"""
        model_cls = get_model()
        try:
            items = self.item_set.filter(status=model_cls.VISIBLE)
            item = items[0]
            image = item.itemimage_set.all()[0]
        except IndexError:
            image = None
        return image

class Item(models.Model):
    HIDDEN = 0
    VISIBLE = 1
    ITEM_CHOICES = (
        (HIDDEN, 'Hidden'),
        (VISIBLE, 'Visible'),
    )
    name = models.CharField(
            max_length=255)
    slug = models.SlugField()
    categories = models.ManyToManyField(
            Category,
            blank=True,
            null=True)
    description = models.TextField(
            blank=True,
            null=True)
    order = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default='5.00')
    created = models.DateTimeField(
            blank=True,
            null=True)
    status = models.PositiveSmallIntegerField(
            choices=ITEM_CHOICES,
            default=c_settings.ITEM_DEFAULT_STATUS)

    objects = managers.ItemManager()

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'%s' % self.name

    @models.permalink
    def get_absolute_url(self):
        return ('ccgallery:item', (), {
            'slug': self.slug,
            })

    @property
    def image(self):
        """returns the first image from the first visible item"""
        model_cls = get_model()
        try:
            image = self.itemimage_set.all()[0]
        except IndexError:
            image = None
        return image


# TODO: test the ordering
class ItemImage(models.Model):
    item = models.ForeignKey(
            Item)
    caption = models.CharField(
            max_length=255,
            blank=True,
            null=True)
    src = ImageWithThumbsField(
                upload_to='ccgallery/itemimages/%Y/%m/%d',
                sizes=c_settings.IMAGE_SIZES)
    order = models.DecimalField(
            max_digits=6,
            decimal_places=2,
            default='5.00')

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.src.url

models.signals.pre_save.connect(
        listeners.created,
        sender=Item,
        dispatch_uid='item_created')
