import click
import shutil
import os

from .base import Generator
from ..utils import (
    _print_step,
    get_path,
    _templates_dir,
    run_command,
    in_directory,
    resolve_template,
)


class StructureGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Generate project base files given the the provided APP_NAME.
        """
        # 1] copy template repostitory to the provided project directory
        _print_step("Copying base sidecar template...")

        shutil.copytree(get_path(_templates_dir, "boilerplate"), project_dir)

        with in_directory(project_dir):
            run_command("git init")

            resolve_template("docker-compose.yaml.template", app_name=app_name)

            with in_directory("api"):
                shutil.move("boilerplate", app_name)
                resolve_template(f"{app_name}/settings.py.template", app_name=app_name)

                resolve_template("Dockerfile.template", app_name=app_name)
                resolve_template("scripts/dev-server.sh.template", app_name=app_name)

                # 2] initialize the poetry project and install expected dependencies
                _print_step("Initializing Poetry project...")

                resolve_template("pyproject.toml", app_name=app_name)
                run_command("poetry install")

                # TODO: remove once accessibility is determined
                _print_step("Initializing repository with Virga submodule...")
                clone_protocol = (
                    "git@github.com:"
                    if os.getenv("GIT_USE_SSH", "False") == "True"
                    else "https://github.com/"
                )
                run_command(
                    "git submodule",
                    "add",
                    f"{clone_protocol}IndicoDataSolutions/virga.git",
                    "lib/virga",
                )
                run_command("poetry add ./lib/virga")
