import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type

from scan_batcher.workflow import Workflow  # base class

_workflows: Dict[str, Type[Workflow]] = {}


def register_workflow(name: str):
    """
    Decorator for registering workflow classes.

    Args:
        name (str): Engine name (e.g., 'vuescan').

    Returns:
        Callable: Class decorator.
    """
    def decorator(cls: Type[Workflow]):
        _workflows[name] = cls
        return cls
    return decorator


def get_workflow(name: str) -> Type[Workflow]:
    """
    Get a registered workflow class by engine name.

    Args:
        name (str): Engine name.

    Returns:
        Type[Workflow]: Workflow class.

    Raises:
        ValueError: If the workflow is not registered.
    """
    if name not in _workflows:
        raise ValueError(f"Unknown workflow: {name}")
    return _workflows[name]


def load_workflows():
    """
    Loads all built-in and external workflow plugins.

    1. Imports all workflow modules in subpackages of the current package.
    2. Loads external plugins via entry points (group 'scan_batcher.workflows').
    """
    # Import all built-in workflow modules
    package_dir = Path(__file__).parent
    for finder, subpkg, ispkg in pkgutil.iter_modules([str(package_dir)]):
        subpkg_path = package_dir / subpkg
        if (subpkg_path / "workflow.py").exists():
            importlib.import_module(f".{subpkg}.workflow", package=__name__)

    # Load external plugins via entry points
    try:
        from importlib.metadata import entry_points
        plugin_group = "scan_batcher.workflows"
        eps = entry_points()
        if hasattr(eps, 'select'):  # Python 3.10+
            plugins = eps.select(group=plugin_group)
        else:
            plugins = eps.get(plugin_group, [])
        for ep in plugins:
            workflow_class = ep.load()
            _workflows[ep.name] = workflow_class
    except ImportError:
        pass


load_workflows()
