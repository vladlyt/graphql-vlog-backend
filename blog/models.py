from enum import Enum

from django.conf import settings
from django.db import models


class PostStatusEnum(Enum):
    DRAFT = 1
    PUBLISHED = 2
    ARCHIVED = 3

    @classmethod
    def label(cls):
        import ipdb;
        ipdb.set_trace()
        return {
            cls.DRAFT.value: 'Draft',
            cls.PUBLISHED.value: 'Published',
            cls.ARCHIVED.value: 'Archived',
        }[cls.value]

    @classmethod
    def choices(cls):
        return (
            (cls.DRAFT.value, 'Draft'),
            (cls.PUBLISHED.value, 'Published'),
            (cls.ARCHIVED.value, 'Archived'),
        )


class Post(models.Model):
    author_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(blank=True, default=None, null=True)
    status = models.SmallIntegerField(choices=PostStatusEnum.choices(), default=PostStatusEnum.DRAFT.value)

    def __str__(self):
        return self.title
