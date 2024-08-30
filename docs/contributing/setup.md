# Environment setup

## Clone repository

- Via https: `git clone https://github.com/realkarych/rxconf.git`
- Via ssh: `git@github.com:realkarych/rxconf.git`
- Via GitHub CLI: `gh repo clone realkarych/rxconf`

## Install poetry

- MacOS / *nix: `curl -sSL https://install.python-poetry.org | python3 -`
- Windows: `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -`

Once Poetry is installed you can execute the following:

```sh
poetry --version
```

## Install dev-dependencies

!!! note
    Assumed that you are in the directory with the project

We implemented two versions of required dependencies:

1. `poetry install` — default dependencies that installs with package via pip.
2. `poetry install --with dev` — dependencies that installs with package via pip AND tools for testing,
deploying documentation, deploying on PyPI.

**You should use the second option.**

## Install Act — local CI

We use [Act](https://github.com/nektos/act) for local CI launching.

It helps us to test RxConf on different environments use local machines instead of GitHub Actions.

After the local CI passes, we contribute code to the origin.

## Build & deploy docs locally

!!! note
    Assumed that you are in the directory with the project and dependencies are already installed.

To build and deploy docs locally, run `mkdocs serve`.

## Build & deploy docs on prod

!!! warning
    Our rule is to not deploy documentation to production manually.

We use a [CI action](https://github.com/realkarych/rxconf/blob/main/.github/workflows/deploy_docs.yml)
that automatically deploys the documentation to production whenever changes are pushed to the `main` branch.

## Deploying on Test PyPI

!!! note
    Requires private access and performs only by core contributors.
    So you can create your own repo on <https://test.pypi.org> and provide token.

Before deploying to the official PyPI repository, we first upload and test our package on Test PyPI.
This allows us to ensure that everything works correctly and to catch any potential issues
before making the package publicly available.

1. **Upload to Test PyPI**:

    - Add Test PyPI repo to poetry conf: `poetry config repositories.testpypi https://test.pypi.org/legacy/`.
    - Add secret to conf: `poetry config pypi-token.testpypi <token>`
    - Publish: `poetry publish --repository testpypi`

2. **Test the package:**

    Install the package from Test PyPI and run tests to ensure everything is working correctly:

    `pip install --index-url https://test.pypi.org/simple/rxconf/`

## Deploying on PyPI

!!! warning
    Our rule is to not deploy library on PyPI from local.

We use a [CI action](https://github.com/realkarych/rxconf/blob/main/.github/workflows/publish.yml)
that automatically deploys the library to <https://pypi.org/project/rxconf/> on new version tag introduction.
