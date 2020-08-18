#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_cli
.. moduleauthor:: Esben Haabendal <esben@geanix.com>

This is the test module for the project's command-line interface (CLI)
module.
"""
# fmt: off
import toggl_dinero.cli as cli
from toggl_dinero import __version__
# fmt: on
from click.testing import CliRunner, Result


# To learn more about testing Click applications, visit the link below.
# http://click.pocoo.org/5/testing/


def test_version_displays_library_version():
    """
    Arrange/Act: Run the `version` subcommand.
    Assert: The output matches the library version.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["version"])
    assert (
        __version__ in result.output.strip()
    ), "Version number should match library version."


def test_verbose_output():
    """
    Arrange/Act: Run the `version` subcommand with the '-v' flag.
    Assert: The output indicates verbose logging is enabled.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["-v", "version"])
    assert (
        "Verbose" in result.output.strip()
    ), "Verbose logging should be indicated in output."


def test_invoice_help():
    """
    Arrange/Act: Run the `invoice --help` subcommand.
    Assert:  The first line of output looks right.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["invoice", "--help"])
    # fmt: off
    assert 'Usage: toggl-dinero invoice' in result.output.strip(), \
        "Help message should contain the command and subcommand name."
    # fmt: on


def test_link_help():
    """
    Arrange/Act: Run the `link --help` subcommand.
    Assert:  The first line of output looks right.
    """
    runner: CliRunner = CliRunner()
    result: Result = runner.invoke(cli.cli, ["link", "--help"])
    # fmt: off
    assert 'Usage: toggl-dinero link' in result.output.strip(), \
        "Help message should contain the command and subcommand name."
    # fmt: on
