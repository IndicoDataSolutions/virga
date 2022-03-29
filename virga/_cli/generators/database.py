import shutil

import click

from ..utils import (
    _print_step,
    _templates_dir,
    get_path,
    in_directory,
    resolve_template,
    run_command,
    run_patch,
)
from .base import Generator


class DatabaseGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Copy the base Alembic and database setup to the project directory.
        """
        # copy the basic alembic structure to the project directory
        _print_step("Creating basic Alembic structure...")

        with in_directory(get_path(project_dir, "api")):
            shutil.copytree(get_path(_templates_dir, "database/alembic"), "alembic")
            shutil.copy2(
                get_path(_templates_dir, "database/alembic.ini"), "alembic.ini"
            )
            resolve_template("alembic/env.py.template", app_name=app_name)

            _print_step("Copying core database plugins...")
            with in_directory(app_name):
                shutil.copytree(
                    get_path(_templates_dir, "database/database"), "database"
                )

                _print_step("Patching generated files...")
                run_patch(
                    get_path(_templates_dir, "database/settings.patch"),
                    "settings.patch",
                )
                run_patch(get_path(_templates_dir, "database/app.patch"), "app.patch")

            run_command("poetry add asyncpg aiodataloader aiofiles")
