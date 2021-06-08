from click.testing import CliRunner
import os
import pytest
from itertools import combinations

from virga._cli.application import virga


def test_virga_new_exists():
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir("full-directory")
        open("full-directory/file.txt", "a").close()
        result = runner.invoke(virga, ["new", "full-directory"])
        assert result.exit_code == 2
        assert result.output.find("already exists") > -1


def test_virga_new():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("new-project")
        assert os.path.isfile("new-project/api/pyproject.toml")
        assert os.path.isfile("new-project/api/poetry.lock")
        assert os.path.isfile("new-project/api/Dockerfile")


cli_args = ["--auth", "--graphql", "--webui", "--database"]


@pytest.mark.parametrize(
    "opts",
    [
        pytest.param(args, id=",".join(args))
        for n in range(len(cli_args))
        for args in combinations(cli_args, n + 1)
    ],
)
def test_virga_new_good_opts(opts):
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project", *opts])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1
