import importlib
import pkgutil

import pytest


def test_import_all_modules():
    package_names = ("tests", "rxconf", )
    for package_name in package_names:
        try:
            module = importlib.import_module(package_name)
        except ImportError as e:
            pytest.fail(f"Failed to import package {package_name}: {e}")

        package_dir = getattr(module, "__path__", None)

        if package_dir is None:
            pytest.fail(f"Failed to determine the directory for package {package_name}")

        for _, module_name, _ in pkgutil.walk_packages(package_dir, package_name + "."):
            try:
                importlib.import_module(module_name)
            except Exception as e:
                pytest.fail(f"Importing {module_name} raised an exception: {e}")
