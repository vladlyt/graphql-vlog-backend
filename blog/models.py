from enum import Enum

from django.conf import settings
from django.db import models


class PostStatus(Enum):
    DRAFT = 1
    PUBLISHED = 2
    ARCHIVED = 3

    def label(self):
        return {
            PostStatus.DRAFT.value: 'Draft',
            PostStatus.PUBLISHED.value: 'Published',
            PostStatus.ARCHIVED.value: 'Archived',
        }[self.value]

    @classmethod
    def choices(cls):
        return (
            (cls.DRAFT.value, 'Draft'),
            (cls.PUBLISHED.value, 'Published'),
            (cls.ARCHIVED.value, 'Archived'),
        )


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published_date = models.DateTimeField(blank=True, default=None, null=True)
    status = models.SmallIntegerField(choices=PostStatus.choices(), default=PostStatus.DRAFT.value)

    def __str__(self):
        return self.title
