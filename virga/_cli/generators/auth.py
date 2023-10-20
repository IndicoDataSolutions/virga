from typing import Any
import os

from typer import Context

from ..utils import (
    _print_step,
    apply_patch,
    copy_template,
    get_path,
    in_directory,
    copy_patch,
)
from .base import Generator


class NoctAuthGenerator(Generator):
    @staticmethod
    def generate(ctx: Context, app_name: str, project_dir: str, **kwargs: Any) -> None:
        """
        Patch the generated base structure to add examples for Noct authentication.
        """
        with in_directory(project_dir):
            # copy the noct app patch to the project directory and apply it
            _print_step("Adding Noct route dependencies...")

            with in_directory(get_path(project_dir, "api", app_name)):
                copy_patch("auth/app.patch")

            _print_step("Patching existing configs...")
            copy_patch("auth/Caddyfile.patch")
            copy_template(
                "auth/docker-compose.patch.template",
                "docker-compose.patch",
                app_name=app_name,
            )
            apply_patch("docker-compose.patch")

            # change the noct route in the webui only if it was generated
            if os.path.exists("webui"):
                copy_template(
                    "auth/app-config.patch.template",
                    "app-config.patch",
                    app_name=app_name,
                )
                apply_patch("app-config.patch")
