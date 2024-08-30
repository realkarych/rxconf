# Hello World app using RxConf

!!! warning
    It is assumed that you are using Python version >= 3.9 and either CPython or PyPy.
    It is assumed that Python is installed in [PATH](https://en.wikipedia.org/wiki/PATH_\(variable\)).

## Prepare project

Create directory `hello_world` and open it.

### On Unix or MacOS

```bash
python -m venv venv && source venv/bin/activate
```

### On Windows

```powershell
python -m venv venv
.\venv\Scripts\activate
```

Then install RxConf:

```shell
pip install rxconf
```

## Prepare config files

### test.yaml

```yaml
app:
    hello_key: Hello
```

### test.toml

```toml
[app]
world_key: World
```

### Add env variable

- On Unix or MacOS: `export APP_EXCLAMATION_MARK=!`
- On Windows: `set APP_EXCLAMATION_MARK=!`

## Let's manipulate them using RxConf

Create `main.py` in the same directory and open it in your favorite code editor / IDE.

### Firstly, we want to load our configs

```python
from rxconf import RxConf

yaml_conf = RxConf.from_file(config_path="test.yaml")
toml_conf = RxConf.from_file(config_path="test.toml")
env_conf = RxConf.from_env()
```

!!! note
    RxConf has single interface for all config-types and interface for loading env-variables.

### So what are `yaml_conf`, `toml_conf` and `env_conf`?

If you try to execute `type()` for them, you will see the heir of `ConfigType`.

This is layer that incapsulate Attributes structure model.

You can `print()` them or call `repr()` to see this structure.

!!! note
    JFYI: we have ConfigResolver that resolves what concrete FileConfigType should be created based on extension.

### Secondly, we want to access variables

```python
hello_var = yaml_conf.app.hello_key
world_var = toml_conf.app.world_key
exclamation_mark = env_conf.app_exclamation_mark
```

!!! note
    RxConf has single interface to create indistinguishable interaction interface for all types of configs.
    So it doesn't matter which register you use, `yaml_conf.APp.WoRld_KEY` will work too.

### So what are `hello_var`, `world_var` and `exclamation_mark`?

If you try to execute `type()` for them, you will see the heir of `AttributeType`.

But there are very smart objects.
They overrides primitive types, operands etc. and your can work with them as primitives:

```python
hello_var + " " + world_var + exclamation_mark == "Hello World!"
```

If you will print the result, you will get `True`.

### Types support & Type casting

So AttributeTypes can be converted to primitives if you want:

`str(hello_var) == "Hello"` — the string representation of `hello_var` value.

#### We supports all types that supports ConfigType you chose

| Type       | Yaml           | Toml           | Json           | Dotenv         |
|------------|----------------|----------------|----------------|----------------|
| `str`      | ✅              | ✅              | ✅              | ✅              |
| `int`      | ✅              | ✅              | ✅              | ✅              |
| `float`    | ✅              | ✅              | ✅              | ✅              |
| `bool`     | ✅              | ✅              | ✅              | ✅              |
| `None`     | ✅              | ❌              | ❌              | ✅              |
| `list`     | ✅              | ✅              | ✅              | ❌              |
| `set`      | ✅              | ❌              | ❌              | ❌              |
| `date`     | ✅              | ✅              | ❌              | ❌              |
| `datetime` | ✅              | ✅              | ❌              | ❌              |

!!! note
    You can iterate via `AttributeType` if it's value's primitive representation is iterable,
    hash it if it's hashable etc.

### Exceptions handling

All exceptions can be raised by RxConf are inherited from `rxconf.exceptions.RxConfError`.

There are some of them:

- Not-existing file: `rxconf.exceptions.ConfigNotFoundError`.
- Unknown extension (that is not specified in any `FileConfigType` registered in `ConfigResolver`): `rxconf.exceptions.InvalidExtensionError`.
- Config with broken schema: `rxconf.exceptions.BrokenConfigSchemaError`.
- Unknown attribute (e.g. `yaml_conf.some.unknown.attr`): `rxconf.exceptions.InvalidAttributeError`.

All existing exceptions your can check in [exceptions.py](https://github.com/realkarych/rxconf/blob/main/rxconf/exceptions.py).

## Observers & Hot-Reload

In-develop...
