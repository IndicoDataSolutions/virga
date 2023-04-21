import click

from .base import Generator
from ..utils import (
    run_patch,
    in_directory,
    resolve_template,
    get_path,
    _print_step,
    _templates_dir,
    run_command,
)


class K8DeploymentGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Copies chart templates and applies the necessary patches to support
        a Helm-based Kubernetes deployment.
        """


class StandaloneDeploymentGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Applies patches to the generated Dockerfile and pyproject.toml files in order
        to support a standalone Gunicorn deployment.
        """
        _print_step("Patching generated files...")
        with in_directory(get_path(project_dir, "api")):
            run_patch(
                get_path(_templates_dir, "deployment/Dockerfile.patch"),
                "Dockerfile.patch",
            )
            resolve_template(
                "Dockerfile.template", app_name=app_name, entrypoint_cmd='"/start.sh"'
            )

            _print_step("Adding Gunicorn deployment dependency...")
            run_command("poetry", "add", "gunicorn[gevent]")
