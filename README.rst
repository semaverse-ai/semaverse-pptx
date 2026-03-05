*semaverse-pptx* is a Python library for creating, reading, and updating PowerPoint (.pptx)
files.

A typical use would be generating a PowerPoint presentation from dynamic content such as
a database query, analytics output, or a JSON payload, perhaps in response to an HTTP
request and downloading the generated PPTX file in response. It runs on any Python
capable platform, including macOS and Linux, and does not require the PowerPoint
application to be installed or licensed.

It can also be used to analyze PowerPoint files from a corpus, perhaps to extract search
indexing text and images.

In can also be used to simply automate the production of a slide or two that would be
tedious to get right by hand, which is how this all got started.

More information is available in the `semaverse-pptx documentation`_.

Browse `examples with screenshots`_ to get a quick idea what you can do with
semaverse-pptx.

.. _`semaverse-pptx documentation`:
   https://semaverse-pptx.readthedocs.org/en/latest/

.. _`examples with screenshots`:
   https://semaverse-pptx.readthedocs.org/en/latest/user/quickstart.html

Developer Hygiene
-----------------

Use ``pre-commit`` locally to run formatting, linting, and type checks before each commit.

1. Sync dev dependencies:

   .. code-block:: bash

      uv sync --extra dev

2. Install git hooks:

   .. code-block:: bash

      uv run pre-commit install

3. Run checks manually across the repository:

   .. code-block:: bash

      uv run pre-commit run --all-files

If you need to unblock formatting/lint-only changes while legacy typing debt is being addressed:

.. code-block:: bash

   SKIP=pyright uv run pre-commit run --all-files
