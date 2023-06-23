import shutil

from typer import Context

from ..utils import _print_step, _templates_dir, get_path, in_directory, run_patch
from .base import Generator


class GraphQLGenerator(Generator):
    @staticmethod
    def generate(ctx: Context, app_name: str, project_dir: str, **kwargs):
        """
        Patch the generated base structure to add GraphQL support.
        """
        # copy the graphql patch to the project directory and apply it
        _print_step("Adding base GraphQL support and schema...")

        with in_directory(get_path(project_dir, "api")):
            with in_directory(app_name):
                shutil.copy2(get_path(_templates_dir, "graphql/gql.py"), "gql.py")

                _print_step("Patching existing code...")

                run_patch(get_path(_templates_dir, "graphql/app.patch"), "app.patch")
