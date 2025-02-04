# Test App using RxConf

!!! info
    It is assumed that you are using Python version >= 3.9 and either CPython or PyPy.

## Prepare project

### 1. Setup dependencies

1. Create virtual environment, use your favourite package manager: `uv`, `poetry`, `pip` etc. *I will use pip*.
2. Install RxConf library: `pip install rxconf`.
3. Check installed dependencies: `pip list`.
!!! tip
    RxConf uses some required dependencies. Сheck them out and make sure their use and licenses are appropriate for you.

!!! note
    RxConf natively support the most popular config formats: `yaml`, `toml`, `ini`, `json`, `dotenv`,
    virtual environments, HashiCorp Vault.

    Some of them require additional deps, that RxConf will ask you to install when you first run the script.
    For example, if you'll use toml config, RxConf will ask you to install `rxconf[toml]` dependency.

### 2. Create config files

- `dummy.yaml`

    ```yaml
    app:
      name: "TestApp"
      version: 1.0
      debug: true
    ```

- `dummy.json`

    ```json
    {
      "app": {
        "name": "TestApp",
        "version": 1.0,
        "debug": true
      }
    }
    ```

  *Notice that they're identical*

### 3. Time to code

**Task to implement:**

1. App impl. must be isolated from concrete config-type impl.
2. App must print it's name every five seconds (to stdout).
3. App must print it's version with name if debug = True.
4. App must print message when the version is increased (and do nothing if decreased). Message: `Increase version: <new_version>`.
5. App must exit when both name and version have changed.

Firsly, let's write the boilerplate:

```python
def exit_on_name_version_changed() -> None:
    print("Exit app!")
    exit(0)

def print_increase_msg(old_version: float, new_version: float) -> None:
    if new_version > old_version:
        print(f"Increase version: {new_version}")

def main() -> None:
    while True:
        <Hmm, some non-ordinary business logic...>
        sleep(5)

if __name__ == "__main__":
    main()
```

So, it doesn't work. We cannot easy control & manipulate the config state.

Let's integrate RxConf to make this App smart!

```python
import rxconf

def exit_on_name_version_changed() -> None:
    print("Exit app!")
    exit(0)

def print_increase_msg(old_version: float, new_version: float) -> None:
    if new_version > old_version:
        print(f"Increase version: {new_version}")

def main() -> None:
    while True:
        sleep(5)

if __name__ == "__main__":
    main()
```
