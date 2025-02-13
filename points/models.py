from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Point(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    exp = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    point = models.ForeignKey('Point', on_delete=models.CASCADE, related_name='articles')

    def __str__(self):
        return self.title
