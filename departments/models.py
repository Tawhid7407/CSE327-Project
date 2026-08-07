from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='bi-heart-pulse',
                            help_text='Bootstrap icon class (e.g. bi-heart-pulse)')
    created_at = models.DateTimeField(auto_now_add=True)



    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
