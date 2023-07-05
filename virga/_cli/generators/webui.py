import shutil
from typing import Any

from typer import Context

from ..utils import (
    _print_step,
    _templates_dir,
    apply_patch,
    copy_template,
    get_path,
    in_directory,
    resolve_template,
    run_command,
    copy_patch,
)
from .base import Generator


class WebUIGenerator(Generator):
    @staticmethod
    def generate(ctx: Context, app_name: str, project_dir: str, **kwargs: Any) -> None:
        """
        Patch the generated base structure to add mini-strat.
        """
        # copy the graphql patch to the project directory and apply it
        _print_step("Adding base Mini-Strat project...")

        with in_directory(project_dir):
            shutil.copytree(get_path(_templates_dir, "webui/boilerplate"), "webui")

            # apply patches for docker-compose and nginx
            _print_step("Patching existing configs...")
            copy_template(
                "webui/docker-compose.patch.template",
                "docker-compose.patch",
                app_name=app_name,
            )
            apply_patch("docker-compose.patch")

            copy_patch("webui/Caddyfile.patch", "Caddyfile.patch")

            with in_directory("webui"):
                resolve_template("package.json.template", app_name=app_name)
                resolve_template("Dockerfile.template", app_name=app_name)

                # install yarn stuff
                _print_step("Installing Yarn dependencies...")
                run_command("yarn", "install")
