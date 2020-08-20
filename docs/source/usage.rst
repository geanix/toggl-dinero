.. _usage:

.. toctree::
    :glob:

*****
Usage
*****

Setup / Configuration
=====================

For now, configuration means setting some environment variables.

Nothing needs to be configured, as everything can be controlled with options
to the `toggl-dinero` tool.

The following environment variables can be set so that less options are needed
when using `toggl-dinero` tool:

* `TOGGL_API_TOKEN` - Toggl API token from your Profile settings on
  https://toggl.com.
* `TOGGL_WORKSPACE` - The name of the Toggl workspace to use.
* `DINERO_CLIENT_ID` - Client ID received after applying as a developer
   with Dinero.
* `DINERO_CLIENT_SECRET` - Client secret received after applying as a
   developer with Dinero.
* `DINERO_ORGANIZATION` - Name of Dinero organization to use.
* `DINERO_API_KEY` - Dinero API key from Dinero integration page.

Link Toggl Client to Dinero Contact
===================================

In order to avoid having to specify both Toggl client and Dinero contact each
time an invoice is created, toggl-dinero stores a reference to a Toggl client
in the `ExternalReference` field of the Dinero contact.

To do this, use something like

.. code-block:: bash

    toggl-dinero link FooBar "FooBar A/S"

to link Toggl client "FooBar" to Dinero contact "FooBar A/S".

Create Invoice
==============

To create an invoice from time entries in Toggl (the actual purpose of this
tool), do something like

.. code-block:: bash

    toggl-dinero invoice FooBar this-month

to create an invoice with all the time entries in this month for Toggl client
named "FooBar".

Supported periods are `today`, `yesterday`, `this-week`, `last-week`,
`this-month`, `last-month`, `this-year`, `last-year`.
