import click
import shutil

from .base import Generator
from ..utils import (
    _print_step,
    get_path,
    _templates_dir,
    resolve_template,
    copy_template,
    run_command,
    in_directory,
    apply_patch,
    run_patch,
)


class WebUIGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
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
                get_path(_templates_dir, "webui/docker-compose.patch.template"),
                "docker-compose.patch",
                app_name=app_name,
            )
            apply_patch("docker-compose.patch")

            run_patch(
                get_path(_templates_dir, "webui/Caddyfile.patch"), "Caddyfile.patch"
            )

            with in_directory("webui"):
                resolve_template("package.json.template", app_name=app_name)
                resolve_template("Dockerfile.template", app_name=app_name)

                # install yarn stuff
                _print_step("Installing Yarn dependencies...")
                run_command("yarn", "install")
