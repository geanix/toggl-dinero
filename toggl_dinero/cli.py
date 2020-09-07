#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.

It can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.

.. currentmodule:: toggl_dinero.cli
.. moduleauthor:: Esben Haabendal <esben@geanix.com>
"""
import logging
import click
from datetime import datetime, timedelta
import calendar
import json
from .__init__ import __version__

from .toggl import TogglAPI
from .dinero import DineroAPI

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels


class Info(object):
    """An information object to pass data between CLI functions."""

    def __init__(self):  # Note: This object must have an empty constructor.
        """Create a new instance."""
        self.verbose: int = 0


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)


# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group(name='toggl-dinero')
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@pass_info
def cli(info: Info, verbose: int):
    """Run toggl-dinero."""
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG
        )
        click.echo(
            click.style(
                f"Verbose logging is enabled. "
                f"(LEVEL={logging.getLogger().getEffectiveLevel()})",
                fg="yellow",
            )
        )
    info.verbose = verbose


@cli.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))


def since_until(period):
    """
    Get start and end dates of a named period.

    :param period: Supported values such as 'today', 'yesterday', 'this-week',
                   and so on.
    :return: tuple of start, end dates of period.
    """
    today = datetime.today()
    if period == 'today':
        return today, today
    elif period == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday, yesterday
    elif period == 'this-week':
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = today + timedelta(days=(6-today.weekday()))
        return start_of_week, end_of_week
    elif period == 'last-week':
        start_of_week = today - timedelta(days=7+today.weekday())
        end_of_week = today + timedelta(days=(6-today.weekday())-7)
        return start_of_week, end_of_week
    elif period == 'this-month':
        start_of_month = today.replace(day=1)
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        end_of_month = today.replace(day=last_day_of_month)
        return start_of_month, end_of_month
    elif period == 'last-month':
        end_of_month = today - timedelta(days=today.day)
        start_of_month = end_of_month.replace(day=1)
        return start_of_month, end_of_month
    elif period == 'this-year':
        start_of_year = today.replace(month=1, day=1)
        return start_of_year, today
    elif period == 'last-year':
        end_of_year = today.replace(month=1, day=1) - timedelta(days=1)
        start_of_year = end_of_year.replace(month=1, day=1)
        return start_of_year, end_of_year


@cli.command()
@click.argument('client')
@click.argument('period',
                type=click.Choice(['today', 'yesterday',
                                   'this-week', 'last-week',
                                   'this-month', 'last-month',
                                   'this-year', 'last-year']),
                default='this-month')
@click.option('--toggl-api-token', envvar='TOGGL_API_TOKEN')
@click.option('--workspace', envvar='TOGGL_WORKSPACE')
@click.option('--billable', type=click.Choice(['yes', 'no', 'both']),
              default='yes')
@click.option('--rounding/--no-rounding', default=True, is_flag=True)
@click.option('--display-hours', type=click.Choice(['decimal', 'minutes']),
              default='decimal')
@click.option('--language', type=click.Choice(['da', 'en']),
              default='da')
@click.option('--dinero-client-id', envvar='DINERO_CLIENT_ID')
@click.option('--dinero-client-secret', envvar='DINERO_CLIENT_SECRET')
@click.option('--dinero-api-key', envvar='DINERO_API_KEY')
@click.option('--dinero-organization', envvar='DINERO_ORGANIZATION')
@click.option('--update', default=False, is_flag=True)
def invoice(client, period, toggl_api_token, workspace,
            billable, rounding, display_hours, language,
            dinero_client_id, dinero_client_secret,
            dinero_api_key, dinero_organization, update):
    """CLI invoice sub-command."""
    toggl = TogglAPI(toggl_api_token)
    client_id = toggl.client_id(client)
    workspace_id = toggl.workspace_id(workspace)
    since, until = since_until(period)
    data = {
        'workspace_id': workspace_id,
        'client_ids': client_id,
        'since': since.strftime('%Y-%m-%d'),
        'until': until.strftime('%Y-%m-%d'),
        'billable': billable,
        'rounding': "on" if rounding else "off",
        'display_hours': display_hours,
    }

    report = toggl.summary_report(data)
    pdf_report = toggl.summary_report_pdf(data)
    with open(f'{client}_report.pdf', mode='wb') as f:
        f.write(pdf_report)

    invoice_currency = None
    invoice_lines = []
    period = f"{since.strftime('%Y-%m-%d')} - {until.strftime('%Y-%m-%d')}"
    if language == 'da':
        header = f'Konsulent ydelser: {period}'
    else:
        header = f'Consultancy services: {period}'
    invoice_lines.append({'Description': header, 'LineType': 'Text'})

    total_hours = 0
    for project in report['data']:
        project_name = project['title']['project']
        assert len(project['total_currencies']) == 1
        currency = project['total_currencies'][0]['currency']
        if invoice_currency is None:
            invoice_currency = currency
        else:
            assert currency == invoice_currency

        for item in project['items']:
            assert item['cur'] == currency
            rate = item['rate']
            ms = item['time']
            hours = ms / (1000 * 60 * 60)
            # round to 2 decimals
            hours = int((hours * 100) + 0.5) / 100
            total_hours += hours
            description = item['title']['time_entry']
            invoice_lines.append({
                'Description': f"{project_name}: {description}",
                'AccountNumber': 1000,
                'Quantity': hours,
                'Unit': 'hours',
                'BaseAmountValue': rate,
            })
        total_hours = int((total_hours * 100) + 0.5) / 100

    if language == 'da':
        header = f'I alt: {total_hours} timer'
    else:
        header = f'Total: {total_hours} hours'
    invoice_lines.append({'Description': header, 'LineType': 'Text'})

    dinero = DineroAPI(dinero_client_id, dinero_client_secret, dinero_api_key,
                       dinero_organization)

    contact = dinero.contact_with_external_reference('toggl', client_id)
    if not contact:
        click.echo(f'Error: Could not find linked Dinero contact: {client_id}')
        return False
    if update:
        invoice = dinero.get_draft_invoice(contact)
        if not invoice:
            click.echo('Error: Could not determine invoice to update')
            return False
        update_product_lines(invoice, invoice_lines)
        dinero.update_invoice(invoice)
    else:
        dinero.create_invoice(contact, invoice_lines,
                              currency=invoice_currency, language=language)


def update_product_lines(invoice, invoice_lines):
    """Update invoice with new hours product lines."""

    def matching_text_line(lines, prefixes):
        for idx, line in enumerate(lines):
            if line['LineType'] != 'Text':
                continue
            for prefix in prefixes:
                if line['Description'].startswith(prefix):
                    return idx
        return None

    header_idx = matching_text_line(invoice['ProductLines'],
                                    ['Konsulent ydelser: ',
                                     'Consultancy services: '])
    if header_idx:
        footer_idx = matching_text_line(
            invoice['ProductLines'][header_idx + 1:],
            ['I alt: ', 'Total: '])
        if footer_idx:
            print(f'{header_idx} - {footer_idx}')
            invoice['ProductLines'] = invoice['ProductLines'][:header_idx] \
                + invoice_lines \
                + invoice['ProductLines'][header_idx + footer_idx + 2:]
        else:
            click.echo('Warning: Could not find matching footer line')
            invoice['ProductLines'] += invoice_lines
    else:
        invoice['ProductLines'] += invoice_lines


@cli.command()
@click.argument('toggl-client')
@click.argument('dinero-contact')
@click.option('--toggl-api-token', envvar='TOGGL_API_TOKEN')
@click.option('--dinero-client-id', envvar='DINERO_CLIENT_ID')
@click.option('--dinero-client-secret', envvar='DINERO_CLIENT_SECRET')
@click.option('--dinero-api-key', envvar='DINERO_API_KEY')
@click.option('--dinero-organization', envvar='DINERO_ORGANIZATION')
def link(toggl_client, dinero_contact,
         toggl_api_token,
         dinero_client_id, dinero_client_secret,
         dinero_api_key, dinero_organization):
    """CLI link sub-command."""
    toggl = TogglAPI(toggl_api_token)
    dinero = DineroAPI(dinero_client_id, dinero_client_secret, dinero_api_key,
                       dinero_organization)
    client_id = toggl.client_id(toggl_client)
    if not client_id:
        click.echo(f'Error: Toggl client not found: {toggl_client}')
    contact_id = dinero.contact_id(dinero_contact)
    if not contact_id:
        click.echo(f'Error: Dinero contact not found: {dinero_contact}')
    contact = dinero.get_contact(contact_id).json()
    extref = contact.get('ExternalReference')
    if extref is not None:
        extref = json.loads(extref)
    else:
        extref = {}
    extref['toggl'] = client_id
    contact['ExternalReference'] = json.dumps(extref)
    dinero.update_contact(contact_id, contact)
