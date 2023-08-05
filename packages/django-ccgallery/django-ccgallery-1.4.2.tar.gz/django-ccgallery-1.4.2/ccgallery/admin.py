from django.contrib import admin
from ccgallery.models import Item, ItemImage, Category
from ccgallery.forms import ItemAdminForm, CategoryAdminForm

class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    prepopulated_fields = {'slug': ('name',)}
    search_fields = (
            'name',
            'description',)
    list_filter = (
            'status',)
    list_display = (
            'name',
            'order',
            'status',)
    list_editable = (
            'order',
            'status',)
    fieldsets = (
        (None, {
            'fields': ('name',
                        'status',
                        'description',
                        ),
            'classes': ('content',),
        }),
        ('Other Stuff', {
            'fields': ('slug',
                        'created'),
            'classes': ('collapse', 'other')
        })
    )


class ImageInline(admin.TabularInline):
    model = ItemImage

class ItemAdmin(admin.ModelAdmin):
    inlines = [ImageInline]
    date_hierarchy = 'created'
    prepopulated_fields = {'slug': ('name',)}
    form = ItemAdminForm
    filter_horizontal = (
            'categories',)
    search_fields = (
            'name',
            'order',)
    list_filter = (
            'status',)
    list_editable = (
            'order',
            'status',)
    list_display = (
            'name',
            'status',
            'order')
    fieldsets = (
        (None, {
            'fields': ('name',
                        'status',
                        'description',
                        'categories'),
            'classes': ('content',),
        }),
        ('Other Stuff', {
            'fields': ('slug',
                        'order',
                        'created'),
            'classes': ('collapse', 'other')
        })
    )

admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
