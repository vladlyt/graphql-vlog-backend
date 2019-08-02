def snake_to_camel_case(name):
    if isinstance(name, str):
        split_name = name.split('_')
        return split_name[0] + "".join(map(str.capitalize, split_name[1:]))
    return name


def get_fields_from_input(input, fields):
    return [input.get(value) for value in fields]
