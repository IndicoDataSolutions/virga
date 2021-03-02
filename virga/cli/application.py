import shutil
import click
import os
import tempfile

from .generators import StructureGenerator, NoctAuthGenerator


_GENERATORS = []


@click.group()
@click.version_option()
def virga():
    """
    Indico's CLI tool for generating templated sidecar applications.
    """
    pass


@virga.command()
@click.option(
    "--force",
    is_flag=True,
    help=f"({click.style('dangerous', fg='red')}) Force app generation even the given project directory is not empty.",
)
@click.option(
    "--auth/--no-auth",
    default=False,
    help="Adds connection middleware to support Noct authentication.",
)
@click.argument("app_path", type=click.Path(writable=True, resolve_path=True))
@click.pass_context
def new(ctx: click.Context, app_path, **kwargs):
    """
    Create a new project called APP_NAME using provided template options.
    """
    print(app_path)
    # santize the requested app name to ensure no overwrites
    if os.path.exists(app_path):
        # if its a file, always reject (ignore --force option)
        if os.path.isfile(app_path):
            raise click.BadParameter(
                click.style(
                    f"'{app_path}' is a file that already exists. Please supply the name of a non-existent file or directory. ",
                    fg="red",
                    bold=True,
                )
            )
        # if its a directory, reject unless --force is provided
        elif not kwargs["force"] and os.listdir(app_path):
            raise click.BadParameter(
                click.style(
                    f"The '{app_path}' directory already exists and is not empty.\n  To create a new project within this directory and overwrite existing files, supply the `--force` flag {click.style('with extreme care', underline=True, reset=False)}.",
                    fg="red",
                    bold=True,
                )
            )

    app_name = os.path.basename(app_path)

    # ensure a quasi-transactional state by generating the project in a temporary
    # directory, then moving it to our desired directory once everything has
    # completed. this is to ensure a clean file directory in case something fails
    # somewhere
    with tempfile.TemporaryDirectory() as project_dir:
        project_dir = os.path.join(project_dir, "tmp")

        try:
            # basic boilerplate generation
            StructureGenerator.generate(ctx, app_name, project_dir)

            # if kwargs["auth"]:
            #     NoctAuthGenerator.generate(ctx, app_name, project_dir)

            # move the full project to the desired location
            shutil.move(project_dir, app_path)
            click.echo("\n=========\n")
            click.secho(
                "Virga application generation complete!\n", bold=True, fg="green",
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
                + click.style(f"\n\n{err}\n", fg="red"),
            )
