import click
from rxconf import RxConf, AttributeType


@click.group()
def main():
    """Main command group for rxconf"""
    pass


@click.command(name='annotate')
@click.argument('conf_path')
@click.argument('dest_path')
def annotate(conf_path, dest_path):
    conf = RxConf.from_file(conf_path)
    annotation = create_annotation(attr_name="AnnotatedConfig", attr=conf._config._root)
    write_pyi_file(dest_path, annotation)


def get_attr_val_type(conf: AttributeType):
    return type(conf._value).__name__


def shift(indent_level: int) -> str:
    return ' ' * (indent_level * 4)


def write_pyi_file(destination: str, conf: str) -> None:
    with open(destination, 'w') as pyi_file:
        pyi_file.write(conf)


def create_annotation(attr_name: str, attr: AttributeType, indent_level: int = 0, result: str = "") -> str:
    if isinstance(attr._value, dict):
        result += shift(indent_level) + f"class {attr_name}:\n"
        for key, attr in attr._value.items():
            result = create_annotation(key, attr, indent_level + 1, result)
    elif isinstance(attr._value, list):
        result += shift(indent_level) + f"{attr_name}: {get_attr_val_type(attr)} = ["
        for i in range(len(attr._value) - 1):
            if isinstance(attr._value[i]._value, str):
                result += f"'{attr._value[i]._value}', "
            else:
                result += f"{attr._value[i]._value}, "
        if isinstance(attr._value[-1]._value, str):
            result += f"'{attr._value[-1]._value}']\n"
        else:
            result += f"{attr._value[-1]._value}]\n"
    elif isinstance(attr._value, set):
        set_values = list(attr._value)
        result += shift(indent_level) + f"{attr_name}: {get_attr_val_type(attr)} = ("
        for i in range(len(set_values) - 1):
            if isinstance(set_values[i]._value, str):
                result += f"'{set_values[i]._value}', "
            else:
                result += f"{set_values[i]._value}, "
        if isinstance(set_values[-1]._value, str):
            result += f"'{set_values[-1]._value}']\n"
        else:
            result += f"{set_values[-1]._value})\n"
    elif isinstance(attr._value, str):
        result += shift(indent_level) + f"{attr_name}: {get_attr_val_type(attr)} = '{attr._value}'\n"
    elif isinstance(attr._value, (int, float)):
        result += shift(indent_level) + f"{attr_name}: {get_attr_val_type(attr)} = {attr._value}\n"
    elif attr._value is None:
        result += shift(indent_level) + f"{attr_name}: {None} = {attr._value}\n"

    return result


main.add_command(annotate)
