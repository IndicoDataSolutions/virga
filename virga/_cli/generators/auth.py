import click
import shutil
import os

from .base import Generator
from ..utils import (
    _print_step,
    get_path,
    _templates_dir,
    in_directory,
    run_command,
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

            with in_directory(get_path(project_dir, "api")):
                # TODO: uncomment when available on pypi
                # run_command("poetry add indico-virga")

                with in_directory(app_name):
                    run_patch(get_path(_templates_dir, "auth/noct.patch"), "noct.patch")

            _print_step("Patching existing configs...")
            run_patch(
                get_path(_templates_dir, "auth/nginx-conf.patch"), "nginx-conf.patch"
            )

            run_patch(
                get_path(_templates_dir, "auth/docker-compose.patch"),
                "docker-compose.patch",
            )

            # change the noct route in the webui only if it was generated
            if os.path.exists("webui"):
                run_patch(
                    get_path(_templates_dir, "auth/webroute.patch"), "webroute.patch"
                )
