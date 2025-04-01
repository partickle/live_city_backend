from rest_framework import serializers
from .models import Category, Point, Article, VisitedPoint


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'color']


class PointSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    article_id = serializers.PrimaryKeyRelatedField(queryset=Article.objects.all(), source='article', required=False, allow_null=True)

    class Meta:
        model = Point
        fields = ['id', 'name', 'category_id', 'latitude', 'longitude', 'exp', 'is_active', 'image', 'article_id']

    def create(self, validated_data):
        category = validated_data.pop('category')
        article = validated_data.pop('article', None)
        point = Point.objects.create(category=category, article=article, **validated_data)
        return point

    def update(self, instance, validated_data):
        category_data = validated_data.pop('category', None)
        article_data = validated_data.pop('article', None)
        if category_data:
            # Если category_data — это объект Category
            if isinstance(category_data, Category):
                instance.category.name = category_data.name
                instance.category.color = category_data.color
            # Если category_data — это словарь
            elif isinstance(category_data, dict):
                instance.category.name = category_data.get('name', instance.category.name)
                instance.category.color = category_data.get('color', instance.category.color)
            instance.category.save()

        if article_data:
            instance.article = article_data

        instance.name = validated_data.get('name', instance.name)
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.exp = validated_data.get('exp', instance.exp)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("image"):
            data["image"] = instance.image.url
        return data


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'content']


class CheckInSerializer(serializers.Serializer):
    point_id = serializers.IntegerField()
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)


class VisitedPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitedPoint
        fields = ["id", "user", "point", "visit_date"]
