Running the test suite
======================

|pp| has a robust test suite at both unit and acceptance levels.
``pytest`` is used for unit tests and ``behave`` for acceptance tests.

Install test dependencies from the project root::

    $ uv sync --extra test

Run unit tests::

    $ uv run pytest -q

Run acceptance tests::

    $ uv run behave --stop

To inspect or run the tox matrix::

    $ tox -av
    $ tox -e py39


Running linters and type checkers
=================================

We use `ruff` for linting and formatting, and `pyright` for static type checking.

Install development dependencies from the project root::

    $ uv sync --extra dev --extra test

Run the linter::

    $ uv run ruff check

Run the type checker::

    $ uv run pyright

We also use `pre-commit` to run checks on every commit. To install the pre-commit hooks::

    $ uv run pre-commit install

To run the checks manually on all files::

    $ uv run pre-commit run --all-files
