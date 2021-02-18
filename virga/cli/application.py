import click
import os


@click.group()
@click.version_option()
def virga():
    """
    Indico's CLI tool for generating templated sidecar applications.
    """
    pass


@virga.command()
@click.option(
    "--database/--no-database",
    default=True,
    help="Adds Alembic and PostgreSQL with asyncio.",
)
@click.option(
    "--auth/--no-auth",
    default=True,
    help="Adds connection middleware to support Noct authentication.",
)
@click.option(
    "--graphql/--no-graphql",
    default=True,
    help="Adds basic GraphQL support through Graphene.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force app generation even the given project directory is not empty.",
)
@click.argument("app_name")
def new(app_name, **kwargs):
    """
    Create a new project called APP_NAME using provided template options.
    """
    # santize the requested app name to ensure no overwrites
    if os.path.exists(app_name):
        # if its a file, always reject (ignore --force option)
        if os.path.isfile(app_name):
            raise click.BadParameter(
                click.style(
                    f"'{app_name}' is a file that already exists. Please supply the name of a non-existent file or directory. ",
                    fg="red",
                    bold=True,
                )
            )
        # if its a directory, reject unless --force is provided
        elif not kwargs["force"] and os.listdir(app_name):
            raise click.BadParameter(
                click.style(
                    f"The '{app_name}' directory already exists and is not empty.\n  To create a new project within this directory and overwrite existing files, supply the `--force` flag {click.style('with extreme care', underline=True, reset=False)}.",
                    fg="red",
                    bold=True,
                )
            )

    pass
