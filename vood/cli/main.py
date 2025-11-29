"""Main CLI entry point for Vood

Provides commands for managing the Playwright render server and other utilities.
"""

import click
from vood.cli.playwright_server_commands import playwright_server
from vood.cli.devserver_commands import serve


@click.group()
@click.version_option(package_name="vood")
def cli():
    """Vood - Programmatic SVG graphics and animation library"""
    pass


# Register command groups
cli.add_command(playwright_server)
cli.add_command(serve)


if __name__ == "__main__":
    cli()
