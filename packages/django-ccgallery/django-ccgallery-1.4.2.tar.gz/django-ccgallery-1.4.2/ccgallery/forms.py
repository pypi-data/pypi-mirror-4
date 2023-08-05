from django import forms
from ccgallery.models import Item, Category

class CategoryAdminForm(forms.ModelForm):

    class Meta:
        model = Category

    class Media:
        css = {
                'screen': ('ccgallery/css/admin.category.css',)
            }

class ItemAdminForm(forms.ModelForm):

    class Meta:
        model = Item

    class Media:
        css = {
                'screen': ('ccgallery/css/admin.item.css',)
            }
