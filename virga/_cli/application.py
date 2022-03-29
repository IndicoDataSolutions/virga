import os
import re
import shutil
import string
import tempfile

import click

from .generators import (
    DatabaseGenerator,
    GraphQLGenerator,
    NoctAuthGenerator,
    StructureGenerator,
    WebUIGenerator,
)


def _to_valid_appname(s):
    """
    Return the given string converted to a string that can be used for a clean
    filename. Remove leading and trailing spaces, numbers, and symbols; convert
    inner spaces, dots, and dashes to underscores, and remove all remaining
    non-alphanumerics.

    https://www.python.org/dev/peps/pep-0008/#package-and-module-names
    """
    s = re.sub(
        r"(?u)[\s.-]",
        "_",
        str(s).strip(string.whitespace + string.punctuation + string.digits),
    )
    return re.sub(r"(?u)[^\w]", "", s)


@click.group()
@click.version_option()
def virga():
    """
    Indico's CLI tool for generating templated sidecar applications.
    """
    pass


@virga.command()
@click.option(
    "--name",
    help="The name of the application to generate. This will be used for both the "
    "Python module and development URL subdomain. If not supplied, this will be parsed"
    " from the provided APP_PATH.",
)
@click.option(
    "--auth/--no-auth",
    default=False,
    help="Adds connection middleware to support Noct authentication.",
)
@click.option(
    "--graphql/--no-graphql",
    default=False,
    help="Adds basic GraphQL support through Graphene.",
)
@click.option("--webui/--no-webui", default=False, help="Adds basic web app template.")
@click.option(
    "--database/--no-database",
    default=False,
    help="Adds Alembic and SQLALchemy with postgresql+asyncpg.",
)
@click.argument("app_path", type=click.Path(writable=True, resolve_path=True))
@click.pass_context
def new(ctx: click.Context, app_path, name: str = None, **kwargs):
    """
    Create a new project using provided template options.

    If no name is supplied, one is derived from the given desired project path
    according to the rules specified in PEP-8. For example:

      - `virga new fruit/banana` generates a new Python module called 'banana' in the
      directory 'fruit/banana'.

      - `virga new fruit/tropical --name mango` generates a new Python module called
      mango in the directory 'fruit/tropical'.

    Rules: https://www.python.org/dev/peps/pep-0008/#package-and-module-names
    """
    # sanitize the requested app name to ensure no overwrites
    if os.path.exists(app_path):
        raise click.BadParameter(
            click.style(
                f"'{app_path}' already exists. To create a new project, supply a path "
                "to a non-existent directory.",
                fg="red",
                bold=True,
            )
        )

    app_name = name or _to_valid_appname(os.path.basename(app_path))

    # ensure a quasi-transactional state by generating the project in a temporary
    # directory, then moving it to our desired directory once everything has
    # completed. this is to ensure a clean file directory in case something fails
    # somewhere
    with tempfile.TemporaryDirectory() as project_dir:
        project_dir = os.path.join(project_dir, "tmp")

        try:
            # basic boilerplate generation
            StructureGenerator.generate(ctx, app_name, project_dir)

            # webapp generation
            if kwargs["webui"]:
                WebUIGenerator.generate(ctx, app_name, project_dir)

            # noct integration
            if kwargs["auth"]:
                NoctAuthGenerator.generate(ctx, app_name, project_dir)

            # graphql integration
            if kwargs["graphql"]:
                GraphQLGenerator.generate(ctx, app_name, project_dir)

            # database setup
            if kwargs["database"]:
                DatabaseGenerator.generate(ctx, app_name, project_dir)

            # move the full project to the desired location
            shutil.move(project_dir, app_path)
            click.echo("\n=========\n")
            click.secho(
                "Virga application generation complete!\n", bold=True, fg="green"
            )
        except Exception as err:
            click.echo(
                "\n=========\n\n"
                + click.style(
                    "Virga application generation failed :(",
                    underline=True,
                    bold=True,
                    fg="red",
                )
                + click.style(f"\n\n{err}\n", fg="red")
            )
