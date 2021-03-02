import click
import shutil
import patch
import os

from .base import Generator
from ..utils import get_path, _templates_dir, in_directory, run_command


class NoctAuthGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Patch the generated base structure to add examples for Noct authentication.
        """
        # 3] copy the noct app patch to the project directory and apply it
        click.secho("  3] Adding Noct middleware...", fg="magenta", bold=True)

        shutil.copy2(
            get_path(_templates_dir, "noct.patch"), get_path(project_dir, app_name)
        )

        with in_directory(project_dir):
            with in_directory(app_name):
                pset = patch.fromfile("noct.patch")

                if pset.apply():
                    os.remove("noct.patch")

            # run_command(f"poetry add indico-virga")
