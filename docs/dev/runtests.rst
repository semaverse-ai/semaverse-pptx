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
