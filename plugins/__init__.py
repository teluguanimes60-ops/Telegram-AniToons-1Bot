"""
plugins/__init__.py

Automatically imports all plugin modules so that
their handlers are registered when the package
is imported.
"""

from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path

_PACKAGE = Path(__file__).parent

__all__: list[str] = []

for module in iter_modules([str(_PACKAGE)]):

    if module.name.startswith("_"):
        continue

    import_module(f"{__name__}.{module.name}")

    __all__.append(module.name)

