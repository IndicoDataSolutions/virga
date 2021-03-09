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


class DatabaseGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Copy the base Alembic and database setup to the project directory.
        """
        # copy the basic alembic structure to the project directory
        _print_step("Creating basic Alembic structure...")

        with in_directory(project_dir):
            shutil.copytree(
                get_path(_templates_dir, "database/alembic"), "alembic",
            )
            shutil.copy2(
                get_path(_templates_dir, "database/alembic.ini"), "alembic.ini"
            )
            resolve_template("alembic/env.py.template", app_name=app_name)

            with in_directory(app_name):
                shutil.copytree(
                    get_path(_templates_dir, "database/database"), "database",
                )
                resolve_template("database/__init__.py.template", app_name=app_name)

            # TODO: uncomment when available on pypi
            # run_command("poetry add indico-virga")
            run_command("poetry add alembic asyncpg")
