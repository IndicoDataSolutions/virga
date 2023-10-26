from abc import ABC, abstractmethod
from typing import Any

from typer import Context


class Generator(ABC):
    """
    The abstract parent class for all generators. Subclasses override the
    `generate` function to perform template operations based on the
    command context and any defined (kw)args.
    """

    @staticmethod
    @abstractmethod
    def generate(ctx: Context, app_name: str, project_dir: str, **kwargs: Any) -> None:
        """Run any generator-specific code."""
        raise NotImplementedError()
