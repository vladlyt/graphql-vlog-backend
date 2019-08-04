from itertools import chain
from textwrap import dedent

import graphene
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models.base import ModelBase
from django.db.models.fields.files import FileField
from graphene.types.mutation import MutationOptions
from graphene_django.registry import get_global_registry
from graphql.error import GraphQLError
from graphql_jwt.exceptions import PermissionDenied

from .types import Error
from .utils import (
    snake_to_camel_case, get_fields_from_input, get_model_name,
    get_output_fields, get_nodes)

registry = get_global_registry()


class BaseInput(graphene.InputObjectType):

    def __init__(self, *args, **kwargs):
        if 'description' not in kwargs:
            raise ImproperlyConfigured('No description provided in Input')
        super().__init__(*args, required=True, **kwargs)


class ModelMutationOptions(MutationOptions):
    exclude = None
    model = None
    return_field_name = None


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
    def _update_mutation_arguments_and_fields(cls, arguments, fields):
        cls._meta.arguments.update(arguments)
        cls._meta.fields.update(fields)

    @classmethod
    def create_error(cls, field: str, message: str):
        return Error(field=snake_to_camel_case(field), message=message)

    @classmethod
    def get_node_or_error(cls, info: graphene.ResolveInfo,
                          global_id: str,
                          field: str,
                          only_type=None):
        """global_id is base64 decoded string with structure <Type>:<id>
        (for example "UserType:2" or "PostType:64")
        """
        if not global_id:
            return None
        node, error = None, None
        try:
            node = graphene.Node.get_node_from_global_id(info, global_id, only_type)
        except (AssertionError, GraphQLError) as e:
            error = cls.create_error(field, str(e))
        else:
            if node is None:
                error = cls.create_error(field, f"Couldn't resolve to a node: {global_id}")
        return node, error

    @classmethod
    def get_nodes_or_error(cls, ids, field, only_type=None):
        instances, error = None, None
        try:
            instances = get_nodes(ids, only_type)
        except GraphQLError as e:
            error = cls.create_error(field, str(e))
        return instances, error

    @classmethod
    def clean_instance(cls, instance):
        """Clean the instance that was created using the input data.

        Once a instance is created, this method runs `full_clean()` to perform
        model fields' validation. Returns errors ready to be returned by
        the GraphQL response (if any occurred).
        """
        errors = []
        try:
            instance.full_clean()
        except ValidationError as validation_errors:
            message_dict = validation_errors.message_dict
            for field in message_dict:
                if hasattr(cls._meta, 'exclude') and field in cls._meta.exclude:
                    continue
                for message in message_dict[field]:
                    errors.append(cls.create_error(field, message))
        return errors

    @classmethod
    def construct_instance(cls, instance, cleaned_data):
        """Fill instance fields with cleaned data.

        The `instance` argument is either an empty instance of a already
        existing one which was fetched from the database. `cleaned_data` is
        data to be set in instance fields. Returns `instance` with filled
        fields, but not saved to the database.
        """
        opts = instance._meta

        for f in opts.fields:
            if any([not f.editable,
                    isinstance(f, models.AutoField),
                    f.name not in cleaned_data]):
                continue
            data = cleaned_data[f.name]
            if data is None:
                # We want to reset the file field value when None was passed
                # in the input, but `FileField.save_form_data` ignores None
                # values. In that case we manually pass False which clears the file.
                if isinstance(f, FileField):
                    data = False
                if not f.null:
                    data = f._get_default()
            f.save_form_data(instance, data)
        return instance


class ModelMutation(BaseMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            arguments: dict = None,
            model: ModelBase = None,
            exclude: list = None,
            return_field_name: str = None,
            _meta=None,
            **options):
        if model is None:
            raise ImproperlyConfigured('`model` must be specified in Meta class of ModelMutation')

        _meta = _meta or ModelMutationOptions(cls)
        exclude = exclude or []
        return_field_name = return_field_name or get_model_name(model)
        arguments = arguments or {}
        fields = get_output_fields(model, return_field_name)

        _meta.model = model
        _meta.return_field_name = return_field_name
        _meta.exclude = exclude
        super().__init_subclass_with_meta__(_meta=_meta, **options)
        cls._update_mutation_arguments_and_fields(arguments=arguments, fields=fields)

    @classmethod
    def clean_input(cls, info, instance, input):
        """Clean input data received from mutation arguments.

        Fields containing IDs or lists of IDs are automatically resolved into
        model instances. `instance` argument is the model instance the mutation
        is operating on (before setting the input data). `input` is raw input
        data the mutation receives. `errors` is a list of errors that occurred
        during mutation's execution.

        Override this method to provide custom transformations of incoming
        data.
        """

        def is_list_of_ids(field_):
            return (isinstance(field_.type, graphene.List)
                    and field_.type.of_type == graphene.ID)

        def is_id_field(field_):
            return (field_.type == graphene.ID
                    or isinstance(field_.type, graphene.NonNull)
                    and field_.type.of_type == graphene.ID)

        input_cls = getattr(cls.Arguments, 'input')
        cleaned_input, errors = {}, []

        for field_name, field in input_cls._meta.fields.items():
            if field_name in input:
                value = input[field_name]
                # handle list of IDs field
                if value is not None and is_list_of_ids(field):
                    instances, error = cls.get_nodes_or_error(value, field_name) if value else [], None
                    cleaned_input[field_name] = instances
                    if error:
                        errors.append(errors)

                # handle ID field
                elif value is not None and is_id_field(field):
                    instance, error = cls.get_node_or_error(info, value, field_name)
                    cleaned_input[field_name] = instance
                    if error:
                        errors.append(error)
                # handle other fields
                else:
                    cleaned_input[field_name] = value
        return cleaned_input, errors

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        opts = instance._meta
        for f in chain(opts.many_to_many, opts.private_fields):
            if not hasattr(f, 'save_form_data'):
                continue
            if f.name in cleaned_data and cleaned_data[f.name] is not None:
                f.save_form_data(instance, cleaned_data[f.name])

    @classmethod
    def user_is_allowed(cls, user, input=None):
        """Determine whether user has rights to perform this mutation."""
        return True

    @classmethod
    def success_response(cls, instance):
        """Return a success response."""
        return cls(**{cls._meta.return_field_name: instance, 'errors': []})

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.save()

    @classmethod
    def mutate(cls, root, info: graphene.ResolveInfo, **data):
        if not cls.user_is_allowed(info.context.user, data):
            raise PermissionDenied()

        id, input = get_fields_from_input(data, ['id', 'input'])
        if id:
            model = registry.get_type_for_model(cls._meta.model)
            instance, error = cls.get_node_or_error(id, 'id', model)
            if error:
                return cls(errors=[error])
        else:
            instance = cls._meta.model()

        cleaned_input, errors = cls.clean_input(info, instance, input)
        instance = cls.construct_instance(instance, cleaned_input)
        clean_instance_errors = cls.clean_instance(instance)
        errors += clean_instance_errors
        if errors:
            return cls(errors=errors)
        cls.save(info, instance, cleaned_input)
        cls._save_m2m(info, instance, cleaned_input)
        return cls.success_response(instance)


class ModelDeleteMutation(ModelMutation):
    class Meta:
        abstract = True

    @classmethod
    def clean_instance(cls, info, instance):
        """Perform additional logic before deleting the model instance.

        Override this method to raise custom validation error and abort
        the deletion process.
        """

    @classmethod
    def mutate(cls, root, info, **data):
        """Perform a mutation that deletes a model instance."""
        user = info.context.user
        if not cls.user_is_allowed(user, data):
            raise PermissionDenied()

        node_id = data.get('id')
        model_type = registry.get_type_for_model(cls._meta.model)
        instance, error = cls.get_node_or_error(info, node_id, 'id', model_type)
        if error:
            return cls(errors=[error])

        errors = cls.clean_instance(info, instance) if instance else []
        if errors:
            return cls(errors=errors)

        db_id = instance.id
        instance.delete()

        # After the instance is deleted, set its ID to the original database's
        # ID so that the success response contains ID of the deleted object.
        instance.id = db_id
        return cls.success_response(instance)
