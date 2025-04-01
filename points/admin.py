from django.contrib import admin
from .models import Category, Point, Article
from django.utils.html import format_html


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


class PointAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude', 'exp', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = "Превью"


admin.site.register(Category, CategoryAdmin)
admin.site.register(Point, PointAdmin)
admin.site.register(Article)
