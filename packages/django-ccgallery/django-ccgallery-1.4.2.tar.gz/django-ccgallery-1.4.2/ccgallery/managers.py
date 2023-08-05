from django.db import models


class CategoryManager(models.Manager):

    def visible(self):
        return super(CategoryManager, self)\
                .get_query_set()\
                .filter(status=self.model.VISIBLE)

    def hidden(self):
        return super(CategoryManager, self)\
                .get_query_set()\
                .filter(status=self.model.HIDDEN)


class ItemManager(models.Manager):

    def for_category(self, category):
        return super(ItemManager, self)\
                .get_query_set()\
                .filter(categories__slug=category.slug,
                       categories__status=category.VISIBLE,
                       status=self.model.VISIBLE)

    def visible(self):
        return super(ItemManager, self)\
                .get_query_set()\
                .filter(status=self.model.VISIBLE)

    def hidden(self):
        return super(ItemManager, self)\
                .get_query_set()\
                .filter(status=self.model.HIDDEN)
