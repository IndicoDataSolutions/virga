import os
import re
import shutil
import string
import tempfile
from pathlib import Path
from importlib.metadata import version

import typer
from rich import print

from .generators import (
    DatabaseGenerator,
    GraphQLGenerator,
    NoctAuthGenerator,
    StructureGenerator,
    WebUIGenerator,
    K8DeploymentGenerator,
    StandaloneDeploymentGenerator,
)


app = typer.Typer()
virga = typer.Typer(rich_markup_mode="markdown")
app.add_typer(virga, name="virga")


def _to_valid_appname(s: str) -> str:
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


def version_callback(ver: bool) -> None:
    if ver:
        print(f"[reset]{version('virga')}")
        raise typer.Exit()


@virga.callback()
def callback(
    ver: bool = typer.Option(
        False,
        "--version",
        is_eager=True,
        callback=version_callback,
        help="Show the current version of Virga.",
    )
) -> None:
    """
    Indico Data's CLI tool for generating sidecar applications. Sidecar apps are not
    direct parts of Indico's IPA releases, but offer additional or custom functionality
    for product or business operations.
    """
    pass


@virga.command()
def new(
    ctx: typer.Context,
    app_path: Path = typer.Argument(..., writable=True, resolve_path=True),
    name: str = typer.Option(
        "",
        help="The name of the application to generate.\n\nThis will be used for both"
        " the Python module and development URL subdomain. If not supplied, one is"
        " derived from the given desired project path according to the rules specified"
        " in PEP-8.",
    ),
    auth: bool = typer.Option(
        False,
        "--auth",
        help="Adds connection middleware to support login integration with an IPA"
        " cluster. This enables shared users between the app and an existing cluster.",
        rich_help_panel="Generators",
    ),
    graphql: bool = typer.Option(
        False,
        "--graphql",
        help="Adds a basic GraphQL route using Graphene via the graphql extra.",
        rich_help_panel="Generators",
    ),
    database: bool = typer.Option(
        False,
        "--database",
        help="Adds Alembic and SQLALchemy support using postgresql and asyncpg via the"
        " database extra.",
        rich_help_panel="Generators",
    ),
    webui: bool = typer.Option(
        False,
        "--webui",
        help="Adds a basic UI template based on React and Stratosphere.\n\nIn addition"
        " to the React application itself, this flag will also generate an nginx-based"
        " Dockerfile for development and to serve as an app ingress when deployed.",
        rich_help_panel="Generators",
    ),
    kubernetes: bool = typer.Option(
        True,
        "--kubernetes/--standalone",
        help="Determines the type of project to generate.\n\nA K8 project will output a"
        " basic and configurable Helm chart. A standalone app will produce an API"
        " Dockerfile that runs Gunicorn as a subprocess-based load balancer.",
        rich_help_panel="Generators",
    ),
) -> None:
    """
    Create a new project, customized using the provided generations options. If
    unsuccessful, projects will be cleaned up automatically to prevent being left in an
    incomplete state. If a `--name` is not specified, one is derived from the desired
    given project path according to the [rules specified in PEP-8](https://www.python.org/dev/peps/pep-0008/#package-and-module-names).
    """  # noqa: E501
    # sanitize the requested app name to ensure no overwrites
    if os.path.exists(app_path):
        raise typer.BadParameter(
            f"'{app_path}' already exists. To create a new project, supply a path to a"
            " non-existent directory."
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
            StructureGenerator.generate(
                ctx,
                app_name,
                project_dir,
                extras=[
                    f"-E{extra}"
                    for extra, enabled in (
                        ("auth", auth),
                        ("graphql", graphql),
                        ("database", database),
                    )
                    if enabled
                ],
            )

            # webapp generation
            if webui:
                WebUIGenerator.generate(ctx, app_name, project_dir)

            # noct integration
            if auth:
                NoctAuthGenerator.generate(ctx, app_name, project_dir)

            # graphql integration
            if graphql:
                GraphQLGenerator.generate(ctx, app_name, project_dir)

            # database setup
            if database:
                DatabaseGenerator.generate(ctx, app_name, project_dir)

            # kubernetes customization
            if kubernetes:
                K8DeploymentGenerator.generate(
                    ctx,
                    app_name,
                    project_dir,
                    webui=webui,
                    auth=auth,
                    database=database,
                )
            else:
                StandaloneDeploymentGenerator.generate(ctx, app_name, project_dir)

            # move the full project to the desired location
            shutil.move(project_dir, app_path)
            print("\n[dim]=========\n")
            print(
                "[bold green]Virga application generation complete! :confetti_ball:\n"
            )
        except Exception as err:
            print("\n[dim]=========\n")
            print(
                "[bold red underline]Virga application generation failed"
                "[not u] :confounded:"
            )
            print(f"[red]\n{err}\n")
            raise typer.Exit(code=1)
