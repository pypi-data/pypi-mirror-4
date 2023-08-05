import ccsitemaps
from ccgallery.models import get_model


Item = get_model()
class GallerySiteMap(ccsitemaps.SiteMap):

    model = Item

    @staticmethod
    def last_mod():
        try:
            last_mod = Item.objects\
                .visible()\
                .order_by('-created')[0]
            return last_mod.created
        except IndexError:
            return None

    @staticmethod
    def get_objects():
        return Item.objects.visible()

ccsitemaps.register(GallerySiteMap)
