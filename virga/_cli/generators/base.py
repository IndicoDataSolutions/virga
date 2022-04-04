from abc import ABC, abstractmethod
from typing import Any

from click import Context


class Generator(ABC):
    """
    The abstract parent class for all generators. Subclasses override the
    `generate` function to perfrom templating operations based on the
    command context and any defiend (kw)args.
    """

    @staticmethod
    @abstractmethod
    def generate(ctx: Context, app_name: str, project_dir: str, **kwargs: Any):
        """Run any generator-specific code."""
        raise NotImplementedError()
