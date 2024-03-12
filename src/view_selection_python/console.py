"""File that'll deal with communication through the CLI."""

import click

from . import __version__


@click.command()
@click.version_option(version=__version__)
def main():
    """The hypermodern Python project."""
    print("TESTING")
