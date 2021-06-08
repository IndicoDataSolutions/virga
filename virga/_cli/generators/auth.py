import click
import os

from .base import Generator
from ..utils import (
    _print_step,
    get_path,
    _templates_dir,
    in_directory,
    copy_template,
    apply_patch,
    run_patch,
)


class NoctAuthGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Patch the generated base structure to add examples for Noct authentication.
        """
        with in_directory(project_dir):
            # copy the noct app patch to the project directory and apply it
            _print_step("Adding Noct route dependencies...")

            with in_directory(get_path(project_dir, "api", app_name)):
                run_patch(get_path(_templates_dir, "auth/app.patch"), "app.patch")

            _print_step("Patching existing configs...")
            run_patch(
                get_path(_templates_dir, "auth/Caddyfile.patch"), "Caddyfile.patch"
            )
            copy_template(
                get_path(_templates_dir, "auth/docker-compose.patch.template"),
                "docker-compose.patch",
                app_name=app_name,
            )
            apply_patch("docker-compose.patch")

            # change the noct route in the webui only if it was generated
            if os.path.exists("webui"):
                copy_template(
                    get_path(_templates_dir, "auth/app-config.patch.template"),
                    "app-config.patch",
                    app_name=app_name,
                )
                apply_patch("app-config.patch")
