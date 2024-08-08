def test_attributes_import():
    try:
        from rxconf import attributes  # noqa: F401
    except Exception as e:
        assert False, f"Importing attributes.py raised an exception: {e}"


def test_config_types_import():
    try:
        from rxconf import config_types  # noqa: F401
    except Exception as e:
        assert False, f"Importing config_types.py raised an exception: {e}"


def test_exceptions_import():
    try:
        from rxconf import exceptions  # noqa: F401
    except Exception as e:
        assert False, f"Importing exceptions.py raised an exception: {e}"


def test_rxconf_import():
    try:
        import rxconf  # noqa: F401
    except Exception as e:
        assert False, f"Importing rxconf entry-point raised an exception: {e}"
