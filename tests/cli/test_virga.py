from click.testing import CliRunner
import os

from virga.cli.application import virga


def test_virga_new_bad():
    runner = CliRunner()

    with runner.isolated_filesystem():
        # non-empty app path
        os.mkdir(f"alive-directory")
        open("alive-directory/file.txt", "a").close()
        result = runner.invoke(virga, ["new", "alive-directory"])
        assert result.exit_code == 2
        assert result.output.find("already exists and is not empty") > -1

        # existing file for app path
        result = runner.invoke(virga, ["new", "alive-directory/file.txt"])
        assert result.exit_code == 2
        assert result.output.find("non-existent file or directory") > -1


def test_virga_new_good():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("new-project")
        assert os.path.isfile("new-project/pyproject.toml")
        assert os.path.isfile("new-project/poetry.lock")
        assert os.path.isfile("new-project/Dockerfile")
