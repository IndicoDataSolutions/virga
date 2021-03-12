import click
import shutil
import patch
import os

from .base import Generator
from ..utils import (
    _print_step,
    get_path,
    _templates_dir,
    run_command,
    in_directory,
)


class GraphQLGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Patch the generated base structure to add GraphQL support.
        """
        # copy the graphql patch to the project directory and apply it
        _print_step("Adding base GraphQL support and schema...")

        with in_directory(project_dir):
            with in_directory(app_name):
                shutil.copy2(get_path(_templates_dir, "graphql/gql.py"), "gql.py")
                shutil.copy2(
                    get_path(_templates_dir, "graphql/graphql.patch"), "graphql.patch"
                )
                pset = patch.fromfile("graphql.patch")

                if not pset.apply():
                    raise Exception("Malformed GraphQL patch. This is a bug :(")

                os.remove("graphql.patch")

            # TODO: uncomment when available on pypi
            # run_command("poetry add indico-virga")
