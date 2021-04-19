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

            shutil.copy2(get_path(_templates_dir, "../../..", "README.md"), "README.md")
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

                # if ssh is enabled, clone and add submodule using bare SSH link
                use_ssh = os.getenv("GITHUB_USE_SSH", "True") == "True"
                submod_protocol = (
                    "git@github.com:" if use_ssh else "https://github.com/"
                )

                # if ssh is disabled, clone repo using https + token (if a token
                # is provided) and add submodule using bare https so the token
                # isn't unintentionally stored and checked in .gitmodules

                clone_protocol = (
                    f"https://{os.getenv('GITHUB_ACCESS_TOKEN', '')}@github.com/"
                    if not use_ssh
                    else submod_protocol
                )

                run_command(
                    "git clone",
                    "--depth=1",
                    "--no-tags",
                    f"{clone_protocol}IndicoDataSolutions/virga.git",
                    "lib/virga",
                )
                run_command(
                    "git submodule",
                    "add",
                    f"{submod_protocol}IndicoDataSolutions/virga.git",
                    "lib/virga",
                )
                run_command("poetry add ./lib/virga")
