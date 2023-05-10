import click
import shutil

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
        with in_directory(project_dir):
            _print_step("Copying and patching Helm templates...")
            shutil.copytree(
                get_path(_templates_dir, "deployment/k8s/boilerplate"), "charts"
            )

            with in_directory("charts"):
                resolve_template("Chart.yaml.template", app_name=app_name)
                resolve_template("values.yaml.template", app_name=app_name)

                # if --webui was specified
                if kwargs["webui"]:
                    shutil.copytree(
                        get_path(_templates_dir, "deployment/k8s/webui/templates/"),
                        "templates/",
                        dirs_exist_ok=True,
                    )

                    run_patch(
                        get_path(
                            _templates_dir, "deployment/k8s/webui/values.yaml.patch"
                        ),
                        "values.yaml.patch",
                    )

                # if --auth was specified
                if kwargs["auth"]:
                    run_patch(
                        get_path(
                            _templates_dir, "deployment/k8s/auth/api-configs.yaml.patch"
                        ),
                        "api-configs.yaml.patch",
                    )
                    run_patch(
                        get_path(
                            _templates_dir, "deployment/k8s/auth/api-secrets.yaml.patch"
                        ),
                        "api-secrets.yaml.patch",
                    )
                    run_patch(
                        get_path(
                            _templates_dir, "deployment/k8s/auth/values.yaml.patch"
                        ),
                        "values.yaml.patch",
                    )

                    # we don't need to patch the auth sections of webui yamls if we
                    # didn't generate the project using the ui flag
                    if kwargs["webui"]:
                        run_patch(
                            get_path(
                                _templates_dir,
                                "deployment/k8s/auth/webui/ui-app-config.yaml.patch",
                            ),
                            "ui-app-config.yaml.patch",
                        )
                        run_patch(
                            get_path(
                                _templates_dir,
                                "deployment/k8s/auth/webui/values.yaml.patch",
                            ),
                            "values.yaml.patch",
                        )

                # if --database was specified
                if kwargs["database"]:
                    shutil.copytree(
                        get_path(_templates_dir, "deployment/k8s/database/templates/"),
                        "templates/",
                        dirs_exist_ok=True,
                    )

                    run_patch(
                        get_path(
                            _templates_dir,
                            "deployment/k8s/database/api-configs.yaml.patch",
                        ),
                        "api-configs.yaml.patch",
                    )

                    run_patch(
                        get_path(
                            _templates_dir,
                            "deployment/k8s/database/api-secrets.yaml.patch",
                        ),
                        "api-secrets.yaml.patch",
                    )

                    run_patch(
                        get_path(
                            _templates_dir, "deployment/k8s/database/values.yaml.patch"
                        ),
                        "values.yaml.patch",
                    )

            _print_step("Patching Dockerfile...")

            with in_directory("api"):
                resolve_template(
                    "Dockerfile.template",
                    app_name=app_name,
                    entrypoint_cmd='"uvicorn", "$APP_MODULE", "--proxy-headers",'
                    ' "--host", "0.0.0.0", "--port", "80"',
                )


class StandaloneDeploymentGenerator(Generator):
    @staticmethod
    def generate(ctx: click.Context, app_name: str, project_dir: str, **kwargs):
        """
        Applies patches to the generated Dockerfile and pyproject.toml files in order
        to support a standalone Gunicorn deployment.
        """
        with in_directory(get_path(project_dir, "api")):
            _print_step("Adding Gunicorn deployment dependency...")
            run_command("poetry", "add", "gunicorn[gevent]")

            _print_step("Patching Dockerfile...")
            run_patch(
                get_path(_templates_dir, "deployment/standalone/Dockerfile.patch"),
                "Dockerfile.patch",
            )
            resolve_template(
                "Dockerfile.template", app_name=app_name, entrypoint_cmd='"/start.sh"'
            )