from django.contrib import admin
from .models import Category, Point


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    search_fields = ('name',)


class PointAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'latitude', 'longitude', 'exp', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category__name')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Point, PointAdmin)
