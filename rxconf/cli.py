import click
from rxconf import RxConf, AttributeType
import pathlib
import re
import os


@click.group()
def main():
    """Main command group for rxconf"""
    pass


@click.command(name='annotate')
@click.argument("script_path")
@click.argument("paths", nargs=-1)
def annotate(script_path, paths):
    """
    Annotate .py file and build .pyi file for that purpose
    """
    script_path = pathlib.Path(script_path)
    folder = script_path.parent
    file_name = script_path.stem  # no extension
    if script_path.suffix != ".py":
        raise ValueError("Rxconf cannot annotate not a .py file")
    result = parse_for_annotations(script_path, *paths)
    dest_file_name = file_name + ".pyi"
    pyi_path = folder / dest_file_name
    write_pyi_file(pyi_path, result)


def parse_for_annotations(script_path: pathlib.Path, *paths) -> str:
    """
    Rewrite lines in .py file where '# rxconf: (async) annotate' appear
    """
    conf_count = 0  # to iterate over conf_paths
    result = ""  # resulting code for .pyi file
    sync_pattern = re.compile(r".*# rxconf: annotate\s*$")  # look for '# rxconf: annotate'
    async_pattern = re.compile(r".*# rxconf: async annotate\s*$")  # look for '# rxconf: async annotate'
    tmp_file = script_path.parent / "tmp_file.py"
    with open(script_path, 'r') as read_file, open(tmp_file, 'w') as write_file:
        write_file.write("from typing import Union\n")
        write_file.write(f"from {script_path.stem} import *\n")
        for idx, line in enumerate(read_file, start=1):
            if sync_pattern.search(line) or async_pattern.search(line):
                if sync_pattern.search(line):
                    variable, new_line = add_annotation(line.rstrip(), "sync")
                else:
                    variable, new_line = add_annotation(line.rstrip(), "async")
                write_file.write(new_line)

                conf = RxConf.from_file(paths[conf_count])
                result = result + create_annotation(variable + "_annotated", conf._config._root)
                if conf_count < len(paths) - 1:
                    result += "\n"
                conf_count += 1
            else:
                write_file.write(line)
    if conf_count != len(paths):
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        raise ValueError("Wrong number of arguments")

    os.replace(tmp_file, script_path)
    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    return result


def add_annotation(line: str, conf_type: str) -> (str, str):
    """
    Add annotation "Union[{var_name}_annotated, RxConf]"
    """
    line = re.sub(r'#.*', '', line)  # Remove comments

    line = re.sub(r'(\w+)\s*:\s*[^=]*=\s*(.*)', r'\1=\2', line)  # Remove type annotations

    match = re.match(r"^(\s*)\s*(\w+)\s*=\s*(.*)", line)
    if match:
        tabs = match.group(1)  # Leading tabs
        var_name = match.group(2)  # Extract variable name
        value = match.group(3).rstrip()  # Extract value after '='

        if conf_type == "async":
            new_annotation = f"Union[{var_name}_annotated, AsyncRxConf]"
            cleaned_line = f"{tabs}{var_name}: {new_annotation} = {value}  # rxconf: async annotate\n"
        else:
            new_annotation = f"Union[{var_name}_annotated, RxConf]"
            cleaned_line = f"{tabs}{var_name}: {new_annotation} = {value}  # rxconf: annotate\n"

        return var_name, cleaned_line

    raise ValueError("Input string does not match expected format")


def get_attr_val_type(conf: AttributeType):
    return type(conf._value).__name__


def shift(indent_level: int) -> str:
    return ' ' * (indent_level * 4)


def write_pyi_file(destination: pathlib.Path, conf: str) -> None:
    with open(destination, 'w') as pyi_file:
        pyi_file.write(conf)


def create_annotation(attr_name: str, attr: AttributeType, indent_level: int = 0, result: str = "") -> str:
    """
    Create annotation class for .pyi file
    """
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
    else:
        result += shift(indent_level) + f"{attr_name}: {None} = {None}\n"

    return result


main.add_command(annotate)
