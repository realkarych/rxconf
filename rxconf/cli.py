from types import NoneType

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
    annotation = extract_class_signature(conf=conf._config._root, indent_level=1)
    annotation = "class AnnotatedConfig:\n" + annotation
    write_pyi_file(dest_path, annotation)


def get_attr_val_type(conf: AttributeType):
    return type(conf._value).__name__


def shift(indent_level: int) -> str:
    return ' ' * (indent_level * 4)


def extract_class_signature(conf: AttributeType, indent_level: int = 0, result: str = "") -> str:
    if isinstance(conf._value, dict):
        for key, val in conf._value.items():
            if isinstance(val._value, dict):
                result += shift(indent_level) + f"class {key}:\n"
            elif isinstance(val._value, str):
                result += shift(indent_level) + f"{key}: {get_attr_val_type(val)} = '{val._value}'\n"
            elif isinstance(val._value, (int, float, NoneType)):
                result += shift(indent_level) + f"{key}: {get_attr_val_type(val)} = {val._value}\n"
            elif isinstance(val._value, list):
                result += shift(indent_level) + f"{key}: {get_attr_val_type(val)} = ["
                for i in range(len(val._value) - 1):
                    if isinstance(val._value[i]._value, str):
                        result += f"'{val._value[i]._value}', "
                    else:
                        result += f"{val._value[i]._value}, "
                if isinstance(val._value[-1]._value, str):
                    result += f"'{val._value[-1]._value}']\n"
                else:
                    result += f"{val._value[-1]._value}]\n"
            elif isinstance(val._value, set):
                set_values = list(val._value)
                result += shift(indent_level) + f"{key}: {get_attr_val_type(val)} = ("
                for i in range(len(set_values) - 1):
                    if isinstance(set_values[i]._value, str):
                        result += f"'{set_values[i]._value}', "
                    else:
                        result += f"{set_values[i]._value}, "
                if isinstance(set_values[-1]._value, str):
                    result += f"'{set_values[-1]._value}']\n"
                else:
                    result += f"{set_values[-1]._value})\n"

            result = extract_class_signature(val, indent_level + 1, result)

    return result


def write_pyi_file(destination: str, conf: str) -> None:
    with open(destination, 'w') as pyi_file:
        pyi_file.write(conf)


main.add_command(annotate)
