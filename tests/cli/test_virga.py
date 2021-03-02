from click.testing import CliRunner
import os

from virga.cli.application import virga


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
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
@pytest.mark.flaky(reruns=1)
=======
>>>>>>> ee500ccdcb48ee4a48393c6c1596eca6f2168aff
>>>>>>> Stashed changes
def test_virga_new_good_nested():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "foo/bar/new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("foo")
        assert os.path.isdir("foo/bar")
        assert os.path.isdir("foo/bar/new-project")
        assert os.path.isfile("foo/bar/new-project/pyproject.toml")
        assert os.path.isfile("foo/bar/new-project/poetry.lock")
        assert os.path.isfile("foo/bar/new-project/Dockerfile")


# single non-existent directory
<<<<<<< Updated upstream
=======
<<<<<<< HEAD
@pytest.mark.flaky(reruns=1)
=======
>>>>>>> ee500ccdcb48ee4a48393c6c1596eca6f2168aff
>>>>>>> Stashed changes
def test_virga_new_good_direct():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1

        assert os.path.isdir("new-project")
        assert os.path.isfile("new-project/pyproject.toml")
        assert os.path.isfile("new-project/poetry.lock")
        assert os.path.isfile("new-project/Dockerfile")


# noct authentication
@pytest.mark.flaky(reruns=1)
def test_virga_new_good_noct():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(virga, ["new", "new-project", "--auth"])
        assert result.exit_code == 0
        assert result.output.find("Virga application generation complete!") > -1
