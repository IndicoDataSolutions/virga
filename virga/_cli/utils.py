import os
import shutil
from contextlib import contextmanager
from fileinput import FileInput
from string import Template
from subprocess import PIPE, CalledProcessError, run
from typing import Union, Optional, Generator

from rich import print as rprint
import patch

Path = Union[str, os.PathLike]


def get_path(*segments: Path) -> str:
    """
    Resolve the given path segments into an absolute real path. Symlinks are
    resolved to their targets during the process.
    """
    return str(os.path.realpath(os.path.join(*segments)))


_templates_dir = get_path(os.path.dirname(__file__), "templates")
_step = 1


def _print_step(msg: str) -> None:
    global _step
    rprint(f"[bold magenta]  {_step}] {msg}")
    _step += 1


def run_command(command: str, *args: str) -> None:
    """
    Run an arbitrary command with arbitrary arguments. STDOUT is preserved
    while STDERR is formatted upon unsuccessful command execution, either at
    the command or OS level.
    """
    cmd = command.split(" ") + list(args)

    # TODO: some commands (ahem poetry) write their stack traces
    # to stdout instead of stderr.
    #
    # SOLUTION: stream stdout to python and print line by line.
    # if command fails, overwrite stdout with ansi and rewrite
    # with the correct error message template
    try:
        # try to the provided command as a subprocess, capturing
        # the stderr if the command fails
        run(cmd, universal_newlines=True, stderr=PIPE, check=True)
    except Exception as err:
        # if the command failed, we only care about its stderr
        if isinstance(err, CalledProcessError):
            err = err.stderr
        errmsg = f"[dim]\n\n{err}" if str(err) else ""

        # the subprocess failed due to an OS exception or an invalid command, so
        # print a nice message instead of throwing a runtime exception
        raise Exception(
            f"The command `{' '.join(cmd)}` was attempted, but failed. The"
            " output was recaptured and is printed." + errmsg
        )


@contextmanager
def in_directory(path: Path) -> Generator[None, None, None]:
    """
    A context manager used to wrap a code block within a change of directory,
    preserving the original working directory and restoring it after block completion.
    """
    curdir = os.getcwd()

    try:
        os.chdir(get_path(path))
        yield
    finally:
        os.chdir(curdir)


def resolve_template(file: Path, **variables: str) -> str:
    """
    Resolves the provided template using the provided variables as placeholders
    and their values. If a placeholder has no found value, it is skipped.

    If file ends in `.template`, the extension is removed.
    """
    if len(variables):
        # avoid the memory overhead of reading the entire template by streaming the
        # file line by line, substituting placeholders where found. by nature, this
        # requires the operation succeed even if placeholders have no value.
        for line in FileInput(file, inplace=True):
            template = Template(line)
            # print the line to stdout, which gets captured and written to the file
            print(template.safe_substitute(variables), end="")

    filepath = get_path(file)
    if filepath.endswith(".template"):
        filepath = shutil.move(filepath, filepath[:-9])

    return filepath


def copy_template(src: Path, dest: Path, **variables: str) -> str:
    """
    Copies a source file to a destination, then resolves the templated destination
    file by passing the provided variables to `resolve_template`.
    """
    shutil.copy2(src, dest)
    return resolve_template(dest, **variables)


def apply_patch(patchfile: str, root: Optional[str] = None) -> None:
    """
    Loads, applies, then deletes the given unified patch file, throwing an error
    if something goes wrong. Specifying a root applies the patch relative to
    that directory, meaning sources and destinations in the patch file are also
    relative to that directory. Patches are applied relative to the current
    working directory by default.
    """
    try:
        pset = patch.fromfile(patchfile)

        if not pset or not pset.apply(root=root):
            raise Exception("Malformed patch. This is a bug :bug:")
    except Exception:
        raise
    finally:
        os.remove(patchfile)


def run_patch(src: str, dest: str) -> None:
    """
    Copies the provided patch file to the destination, then applies the patch
    using `apply_patch`. The patch is always applied relative to the parent directory
    of the destination, so patches must also specify their sources/destination relative
    to the parent of destination.
    """
    shutil.copy2(src, dest)
    apply_patch(dest, root=os.path.dirname(dest))
