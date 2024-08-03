# Contributing Guidelines

Thank you for your interest in contributing to RxConf!

Please take a moment to review the following guidelines before submitting your contribution.

## Table of Contents

- [Getting Started](#getting-started)
- [Submitting Contributions](#submitting-contributions)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Getting Started

To get started with contributing, please follow these steps:

1. Fork the repository.
2. Clone the forked repository to your local machine.
3. Create a new branch for your contribution.
4. Make your changes and commit them.
5. Push your changes to your forked repository.
6. Create a pull request to the main repository.
7. Fix all failed tests.
8. Write changelog — difference that you.

## Submitting Contributions

When submitting your contribution, please ensure the following:

- Minimized count of commits.
- Your code follows our code style guidelines.
- Your changes are well-documented and include any necessary updates to the project's documentation.
- Your changes do not introduce any breaking changes or regressions.
- Provided descriptive commits' titles. Use emoji notation:

| Topic                      | Alias                                         |
|----------------------------|-----------------------------------------------|
| Version tag                | :bookmark: `:bookmark:`                       |
| New feature                | :sparkles: `:sparkles:`                       |
| Bugfix                     | :bug: `:bug:`                                 |
| Documentation              | :books: `:books:`                             |
| Performance                | :racehorse: `:racehorse:`                     |
| Tests                      | :white_check_mark: `:white_check_mark:`       |
| General update             | :rocket: `:rocket:`                           |
| Improve format/structure   | :art: `:art:`                                 |
| Refactor code              | :hammer: `:hammer:`                           |
| Removing code/files        | :fire: `:fire:`                               |
| Continuous Integration     | :construction_worker: `:construction_worker:` |
| Security                   | :lock: `:lock:`                               |
| Upgrading dependencies     | :arrow_up: `:arrow_up:`                       |
| Downgrading dependencies   | :arrow_down: `:arrow_down:`                   |
| Critical hotfix            | :ambulance: `:ambulance:`                     |
| Adding CI build system     | :construction_worker: `:construction_worker:` |
| Configuration files        | :wrench: `:wrench:`                           |
| Reverting changes          | :rewind: `:rewind:`                           |
| Breaking changes           | :boom: `:boom:`                               |
| Movements                  | :truck: `:truck:`                             |

## Code Style

We follow a specific code style in our project. Please make sure to adhere to the following guidelines:

- Follow all PEP8 guidelines.
- Use meaningful variable and function names.
- Avoid of addition comments.
- Add docstrings for all public interfaces.
- Follow the main Clean Code patterns.

## Testing

We highly encourage contributors to write tests for their code.
Please ensure that your changes are thoroughly tested and that all existing tests pass.

Our goal is to have 100% of code coverage (for public interfaces).

## Documentation

Documentation deploys automatically via pushing to main.

Improving the project's documentation is always appreciated.
If you make any changes that require updates to the documentation, please include those updates in your contribution.

## Issue Reporting

If you encounter any issues or have any suggestions for improvement, please open an issue on our
[issue tracker](https://github.com/realkarych/rxconf/issues).

Provide as much detail as possible to help us understand and address the problem.
