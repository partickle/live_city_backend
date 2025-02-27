from django.db import models


class Statistics(models.Model):
    total_users = models.IntegerField(default=0)
    total_visits = models.IntegerField(default=0)
    visits_per_point = models.JSONField(default=dict)
    top_points = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Statistics (last updated: {self.created_at})"

    @classmethod
    def update_statistics(cls, total_users, total_visits, visits_per_point, top_points):

        statistics, created = cls.objects.get_or_create(id=1)
        statistics.total_users = total_users
        statistics.total_visits = total_visits
        statistics.visits_per_point = visits_per_point
        statistics.top_points = top_points
        statistics.save()
        return statistics
