from django.conf import settings
from django.db import models


class Post(models.Model):
    DRAFT = 1
    PUBLISHED = 2
    ARCHIVED = 3
    STATUSES = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, default=None, null=True)
    status = models.SmallIntegerField(choices=STATUSES, default=DRAFT)

    def __str__(self):
        return self.title
