from click.testing import CliRunner
import os
import pytest
from itertools import combinations

from virga._cli.application import virga


# non-empty app path
def test_virga_new_bad_non_empty():
    runner = CliRunner()

    with runner.isolated_filesystem():
        os.mkdir(f"full-directory")
        open("full-directory/file.txt", "a").close()
        result = runner.invoke(virga, ["new", "full-directory"])
        assert result.exit_code == 2
        assert result.output.find("already exists and is not empty") > -1


# existing file for app path
def test_virga_new_bad_file():
    runner = CliRunner()

    with runner.isolated_filesystem():
        open("file.txt", "a").close()
        result = runner.invoke(virga, ["new", "file.txt"])
        assert result.exit_code == 2
        assert result.output.find("non-existent file or directory") > -1


# nested non-existent directories
def test_virga_new_good_nested():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "foo/bar/new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("foo")
        assert os.path.isdir("foo/bar")
        assert os.path.isdir("foo/bar/new-project")
        assert os.path.isfile("foo/bar/new-project/api/pyproject.toml")
        assert os.path.isfile("foo/bar/new-project/api/poetry.lock")
        assert os.path.isfile("foo/bar/new-project/api/Dockerfile")


# single non-existent directory
def test_virga_new_good_direct():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("new-project")
        assert os.path.isfile("new-project/api/pyproject.toml")
        assert os.path.isfile("new-project/api/poetry.lock")
        assert os.path.isfile("new-project/api/Dockerfile")


cli_args = ["--auth", "--graphql", "--webui"]


@pytest.mark.parametrize(
    "opts",
    [
        pytest.param(args, id=",".join(args).replace("--", ""))
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
