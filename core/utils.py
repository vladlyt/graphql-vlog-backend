import graphene
from django.core.exceptions import ImproperlyConfigured
from graphene_django.registry import get_global_registry
from graphql import GraphQLError
from graphql_relay import from_global_id

registry = get_global_registry()


def snake_to_camel_case(name):
    if isinstance(name, str):
        split_name = name.split('_')
        return split_name[0] + "".join(map(str.capitalize, split_name[1:]))
    return name


def get_fields_from_input(input, fields):
    return [input.get(value) for value in fields]


def get_model_name(model):
    """Return name of the model with first letter lowercase."""
    model_name = model.__name__
    return model_name[:1].lower() + model_name[1:]


def get_output_fields(model, return_field_name):
    """Return mutation output field for model instance."""
    model_type = registry.get_type_for_model(model)
    if not model_type:
        raise ImproperlyConfigured(f'Unable to find type for model {model.__name__} in graphene registry')
    return {
        return_field_name: graphene.Field(model_type)
    }


def get_nodes(ids, graphene_type=None):
    """Return a list of nodes.

    If the `graphene_type` argument is provided, the IDs will be validated
    against this type. If the type was not provided, it will be looked up in
    the Graphene's registry. Raises an error if not all IDs are of the same
    type.
    """
    pks, types, invalid_ids = [], [], []
    error_msg = "Could not resolve to a nodes with the global id list of '{}'"
    for graphql_id in ids:
        if graphql_id:
            try:
                _type, _id = from_global_id(graphql_id)
            except UnicodeDecodeError:
                invalid_ids.append(graphql_id)
            else:
                if graphene_type and str(graphene_type) != _type:
                    raise ValueError(f'Must receive an {graphene_type._meta.name} id.')
                pks.append(_id)
                types.append(_type)
    if invalid_ids:
        raise GraphQLError(error_msg.format(invalid_ids))

    # If `graphene_type` was not provided, check if all resolved types are
    # the same. This prevents from accidentally mismatching IDs of different
    # types.
    if types and not graphene_type:
        # get type by name
        type_name = types[0]
        for model, _type in registry._registry.items():
            if _type._meta.name == type_name:
                graphene_type = _type
                break

    nodes = list(graphene_type._meta.model.objects.filter(pk__in=pks))
    nodes.sort(key=lambda e: pks.index(str(e.pk)))  # preserve order in pks
    if not nodes:
        raise GraphQLError(error_msg.format(ids))
    nodes_pk_list = [str(node.pk) for node in nodes]
    for pk in pks:
        assert pk in nodes_pk_list, (
            'There is no node of type {} with pk {}'.format(_type, pk))
    return nodes


def get_database_id(info, node_id, only_type):
    """Get a database ID from a node ID of given type."""
    _type, _id = graphene.relay.Node.from_global_id(node_id)
    graphene_type = info.schema.get_type(_type).graphene_type
    if graphene_type != only_type:
        raise AssertionError('Must receive a {only_type._meta.name} id.')
    return _id
