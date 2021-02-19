import os
import click
from subprocess import run, PIPE, CalledProcessError
from contextlib import contextmanager
import shutil
from fileinput import FileInput
from string import Template


def get_path(*segments: str):
    """
    Resolve the given path segments into an absolute real path. Symlinks are
    resolved to their targets during the process.
    """
    return os.path.realpath(os.path.join(*segments))


_templates_dir = get_path(os.path.dirname(__file__), "templates")


def run_command(command: str, *args: str):
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
        err = click.style(f"\n\n{err}", dim=True) if str(err) else ""

        # the subprocess failed due to an OS exception or an invalid command, so
        # print a nice message instead of throwing a runtime exception
        click.get_current_context().fail(
            click.style(
                f"The command `{' '.join(cmd)}` was attempted, but failed. The output was recaptured and is printed."
            )
            + err
        )


@contextmanager
def in_directory(path):
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


def resolve_template(file: str, **variables):
    """
    Copies a source file to a destination. If the source file is a template, the
    provided variables are used as placeholders and values with which to substitute.
    If a placeholder has no found value, it is skipped.
    """
    if len(variables):
        # avoid the memory overhead of reading the entire template by streaming the
        # file line by line, substituting placeholders where found. by nature, this
        # requires the operation succeed even if placeholders have no value.
        for line in FileInput(file, inplace=True):
            template = Template(line)
            # print the line to stdout, which gets captured and written to the file
            print(template.safe_substitute(variables), end="")

    if file.endswith(".template"):
        shutil.move(file, file[:-9])


def copy_template(src: str, dest: str, **variables):
    """
    Copies a source file to a destination, then resolves the templated destination
    file by passing the provided variables to `resolve_template`.
    """
    shutil.copy2(src, dest)
    resolve_template(dest, **variables)
