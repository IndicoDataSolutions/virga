from typing import List, Any

import shutil

from typer import Context

from ..utils import (
    _print_step,
    _templates_dir,
    get_path,
    in_directory,
    resolve_template,
    run_command,
)
from .base import Generator


class StructureGenerator(Generator):
    @staticmethod
    def generate(
        ctx: Context,
        app_name: str,
        project_dir: str,
        extras: List[str] = [],
        **kwargs: Any,
    ) -> None:
        """
        Generate project base files given the the provided APP_NAME.
        """
        # 1] copy template repository to the provided project directory
        _print_step("Copying base sidecar template...")

        shutil.copytree(get_path(_templates_dir, "boilerplate"), project_dir)

        with in_directory(project_dir):
            resolve_template("docker-compose.yaml.template", app_name=app_name)

            with in_directory("api"):
                shutil.move("boilerplate", app_name)
                resolve_template(f"{app_name}/settings.py.template", app_name=app_name)

                # 2] initialize the poetry project and install expected dependencies
                _print_step("Initializing Poetry project...")

                resolve_template("pyproject.toml", app_name=app_name)
                run_command("poetry", "install")
                run_command(
                    "poetry",
                    "add",
                    "git+https://github.com/IndicoDataSolutions/virga.git#main",
                    *sorted(extras),
                )
