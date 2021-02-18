from abc import ABC, abstractmethod
import click
from typing import Any
from subprocess import run, PIPE, CalledProcessError


class Generator(ABC):
    """
    The abstract parent class for all generators. Subclasses override the
    `generate` function to perfrom templating operations based on the
    command context and any defiend (kw)args.
    """

    @staticmethod
    @abstractmethod
    def generate(ctx: click.Context, *args: Any, **kwargs: Any):
        """ Run any generator-specific code. """
        pass


def _run_command(command: str, *args: str):
    cmd = command.split(" ") + list(args)

    try:
        # try to the provided command as a subprocess, capturing
        # the stderr if the command fails
        run(cmd, universal_newlines=True, stderr=PIPE, check=True)
    except Exception as err:
        # if the command failed, we only care about its stderr
        if isinstance(err, CalledProcessError):
            err = err.stderr

        # the subprocess failed due to an OS exception or an invalid command, so
        # print a nice message instead of throwing a runtime exception
        click.echo(
            click.style(
                f"The command `{' '.join(cmd)}` was attempted, but failed. The output was recaptured and is printed below:",
                bold=True,
                fg="red",
            )
            + click.style(f"\n\n\t{err}\n", fg="red")
        )
