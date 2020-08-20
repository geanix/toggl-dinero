.. _getting_started_dev:

.. toctree::
    :glob:

***************
Getting Started
***************

This section provides instructions for setting up your development environment.  If you follow the
steps from top to bottom you should be ready to roll by the end.


Get the Source
==============

The source code for the `toggl-dinero` project lives at
`github <https://github.com/geanix/toggl-dinero>`_.  
You can use `git clone` to get it.

.. code-block:: bash

   git clone https://github.com/geanix/toggl-dinero

Create the Virtual Environment
==============================

You can create a virtual environment and install the project's dependencies using :ref:`make <make>`.

.. code-block:: bash

    make venv
    make install
    source venv/bin/activate

Toolbox Environment
===================

`Toolbox <https://github.com/containers/toolbox>`_ is container based method for managing development
environments, which you might want to use instead of Python virtual environments.
In order to use this, you need to have Toolbox and `Podman <https://podman.io/>`_ in your host OS.
Depending on your host OS, this might require more or less effort.

To create a Toolbox container for working with this project, use

.. code-block:: bash

    podman build -t toggl-dinero-toolbox -f Dockerfile.toolbox
    toolbox create -i toggl-dinero-toolbox -c toggl-dinero

To enter the toggl-dinero Toolbox environment, use

.. code-block:: bash

    toolbox enter toggl-dinero

To play around with the code, you can install it in development mode, which will alow running the
toggl-dinero command with the code just as it is.  An entry-point wrapper will be installed to
/usr/local/bin and will use the .py files directly from the Git working copy (checkout).

.. code-block:: bash

    sudo python setup.py develop
    toggl-dinero version

Try It Out
==========

One way to test out the environment is to run the tests.  You can do this with the `make test`
target.

.. code-block:: bash

    make test

If the tests run and pass, you're ready to roll.

Getting Answers
===============

Once the environment is set up, you can perform a quick build of this project
documentation using the `make answers` target.

.. code-block:: bash

    make answers
