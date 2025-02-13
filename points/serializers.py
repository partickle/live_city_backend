from rest_framework import serializers
from .models import Category, Point, Article


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color']


class PointSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Point
        fields = ['id', 'name', 'category', 'latitude', 'longitude', 'exp', 'is_active']

    def create(self, validated_data):
        category_data = validated_data.pop('category')
        category = Category.objects.create(**category_data)
        point = Point.objects.create(category=category, **validated_data)
        return point

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        if category_data:
            instance.category.name = category_data.get('name', instance.category.name)
            instance.category.color = category_data.get('color', instance.category.color)
            instance.category.save()
        instance.name = validated_data.get('name', instance.name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.exp = validated_data.get('exp', instance.exp)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'point']