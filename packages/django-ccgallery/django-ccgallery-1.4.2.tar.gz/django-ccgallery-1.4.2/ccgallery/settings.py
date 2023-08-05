from django.conf import settings


"""The default status for items"""
ITEM_DEFAULT_STATUS = getattr(
        settings,
        'CCGALLERY_ITEM_DEFAULT_STATUS',
        1)

"""The default status for categories"""
CATEGORY_DEFAULT_STATUS = getattr(
        settings,
        'CCGALLERY_CATEGORY_DEFAULT_STATUS',
        1)

"""If false then the bundled model will be used"""
MODEL = getattr(
        settings,
        'CCGALLERY_MODEL',
        False)

"""The image sizes for the gallery item"""
IMAGE_SIZES = getattr(
        settings,
        'CCGALLERY_IMAGE_SIZES',
        (   (200,200),
            (640, 480),
            (1200, 960)))

"""The markup language to use"""
MARKUP_LANGUAGE = getattr(
        settings,
        'CCGALLERY_MARKUP_LANGUAGE',
        'markdown')
