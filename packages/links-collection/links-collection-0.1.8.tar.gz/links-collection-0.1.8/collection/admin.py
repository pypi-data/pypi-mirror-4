from django.contrib import admin

from .models import Category, Product, Photo

class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        PhotoInline,
    ]
    list_display = ('reference', 'name', 'num_views', 'featured', 'sold', 'category')
    list_display_links = ('reference', 'name')
    list_editable = ('featured', 'sold', 'category')
    search_fields = ('reference', 'name')
    ordering = ['name']


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Photo)
