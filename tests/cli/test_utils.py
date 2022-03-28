import os
import shutil

import click
import pytest
from click.exceptions import UsageError
from virga._cli.utils import (
    copy_template,
    get_path,
    in_directory,
    resolve_template,
    run_command,
)


def test_get_path(tmpdir):
    p1 = tmpdir.mkdir("sub").join("file0.txt")
    p2 = tmpdir.join("file0")

    os.symlink(p1, p2)

    assert get_path(*os.path.split(p2)) == p1


def mock_abort():
    raise UsageError("MOCK ERR")


def test_run_command(monkeypatch, tmpdir):
    tempfile = tmpdir.join("file0.txt")

    run_command("touch", tempfile)
    assert os.path.exists(tempfile)

    monkeypatch.setattr(click, "get_current_context", mock_abort)
    with pytest.raises(UsageError):
        run_command("xxxxxx")  # invalid command, OS error

    with pytest.raises(UsageError):
        run_command("ls" "doesnt-exists")  # failed command, runtime error

    run_command("rm", tempfile)
    assert not os.path.exists(tempfile)


def test_directory(tmp_path):
    curdir = os.getcwd()

    with in_directory(tmp_path):
        assert os.getcwd() == os.fspath(tmp_path)

    assert curdir == os.getcwd()


@pytest.fixture(scope="session")
def mock_template():
    return os.path.join(os.path.dirname(__file__), "templates/mockfile.txt.template")


def test_resolve_template(mock_template, tmp_path):
    temp = tmp_path / "mockfile.txt.template"
    shutil.copy2(mock_template, temp)

    temp = resolve_template(temp, listener="world")

    assert os.path.exists(temp)

    with open(temp, "r") as f:
        assert f.read() == "hello world!"


def test_copy_template(mock_template, tmp_path):
    temp = tmp_path / "mockfile.txt"

    temp = copy_template(mock_template, temp, listener="outside world")

    assert os.path.exists(temp)

    with open(temp, "r") as f:
        assert f.read() == "hello outside world!"
