# Hello World app using RxConf

!!! warning
    It is assumed that you are using Python version >= 3.9 and either CPython or PyPy.
    It is assumed that Python is installed in [https://en.wikipedia.org/wiki/PATH_(variable)](PATH).

## Prepare project

Create directory `hello world` and open it.

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

Firstly, we want to load our configs:

```python
from rxconf import RxConf

yaml_conf = RxConf.from_file(config_path="test.yaml")
toml_conf = RxConf.from_file(config_path="test.toml")
env_conf = RxConf.from_env()
```

!!! note
    RxConf has single interface for all config-types and interface for loading env-variables.

Secondly, we want to access variables:

```python
hello_var = yaml_conf.app.hello_key
world_var = toml_conf.app.world_key
exclamation_mark = env_conf.app_exclamation_mark
```

!!! note
    RxConf has single interface to access all variables for all types of configs.
    So it doesn't matter which register you use, `yaml_conf.APp.WoRld_KEY` will work too.

If you try to execute `type()` for any of vars, you will see the heir of `AttributeType`.

But there are very smart objects.
They overrides primitive types, operands etc. and your can work with them as primitives:

```python
hello_var + " " + world_var + exclamation_mark == "Hello World!"
```

If you will print the result, you will get `True`.

So AttributeTypes can be converted to primitives if you want:

`str(hello_var)` — the string representation of `hello_var` value.

We supports all types that supports config you chose.

You can iterate via `AttributeType` if it's value is iterable, hash it if it's hashable etc.

## Observers & Hot-Reload

In-develop...
