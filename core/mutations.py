from textwrap import dedent

import graphene
from django.core.exceptions import ImproperlyConfigured

from .types import Error
from .utils import snake_to_camel_case


class BaseMutation(graphene.Mutation):
    errors = graphene.List(
        graphene.NonNull(Error),
        description='List of errors that occurred executing the mutation'
    )

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, description=None, **options):
        if not description:
            raise ImproperlyConfigured('No description provided in Meta')
        description = dedent(description)
        super().__init_subclass_with_meta__(description=description, **options)

    @classmethod
    def create_error(cls, field: str, message: str):
        return Error(field=snake_to_camel_case(field), message=message)
