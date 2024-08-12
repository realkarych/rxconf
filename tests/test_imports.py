import importlib
import os
import pytest


def test_import_all_modules():
    package_name = "rxconf"
    module = importlib.import_module(package_name)
    package_dir = getattr(module, "__file__", None)

    if package_dir is None:
        pytest.fail(f"Failed to determine the directory for package {package_name}")

    package_dir = os.path.dirname(package_dir)

    for filename in os.listdir(package_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{package_name}.{filename[:-3]}"
            try:
                importlib.import_module(module_name)
            except Exception as e:
                pytest.fail(f"Importing {module_name} raised an exception: {e}")
