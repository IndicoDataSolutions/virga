import os
from itertools import combinations
from unittest.mock import MagicMock, patch
import subprocess

import pytest
from click.testing import CliRunner

from virga._cli.application import virga


@pytest.fixture
def run_command_patch():
    mock = MagicMock()
    with patch("virga._cli.generators.structure.run_command", mock):
        with patch("virga._cli.generators.webui.run_command", mock):
            with patch("virga._cli.generators.database.run_command", mock):
                yield mock


def test_virga_new_exists():
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("full-directory")
        open("full-directory/file.txt", "a").close()
        result = runner.invoke(virga, ["new", "full-directory"])
        assert result.exit_code == 2
        assert result.output.find("already exists") > -1


def test_virga_new(run_command_patch):
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("new-project")
        assert os.path.isfile("new-project/api/pyproject.toml")
        assert os.path.isfile("new-project/api/Dockerfile")

        run_command_patch.assert_any_call("poetry", "install")
        run_command_patch.assert_any_call(
            "poetry", "add", "git+https://github.com/IndicoDataSolutions/virga.git#main"
        )


cli_args = sorted(["--auth", "--graphql", "--webui", "--database", "--standalone"])


@pytest.mark.parametrize(
    "opts",
    [
        pytest.param(args, id=",".join(args))
        for n in range(len(cli_args))
        for args in combinations(cli_args, n + 1)
    ],
)
def test_virga_new_good_opts(opts, run_command_patch):
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project", *opts])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        expected_extras = [f"-E{o[2:]}" for o in opts if o != "webui"]
        run_command_patch.assert_any_call("poetry", "install")
        run_command_patch.assert_any_call(
            "poetry",
            "add",
            "git+https://github.com/IndicoDataSolutions/virga.git#main",
            *expected_extras,
        )

        if "--webui" in opts:
            run_command_patch.assert_any_call("yarn", "install")

        # kube is default
        if "--standalone" not in opts:
            subprocess.run(["helm", "template", "new-project/charts"], check=True)
