from django.db import models
from django.utils.timezone import now

from authorization.models import User


class Category(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title


class Point(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="points")
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    exp = models.IntegerField()
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='point_images/', null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True, related_name="points")

    def __str__(self):
        return self.name


class VisitedPoint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(default=now)

    class Meta:
        unique_together = ('user', 'point')

    def __str__(self):
        return f"{self.user.email} - {self.point.name}"
