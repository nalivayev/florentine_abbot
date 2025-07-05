from abc import ABC, abstractmethod

from scan_batcher.recorder import Recorder


class Workflow(ABC):
    """
    Abstract base class for all workflow plugins.
    All workflow classes must inherit from this class and implement the __call__ method.
    """

    class Exception(Exception):
        """Custom exception for workflow errors."""
        pass

    @abstractmethod
    def __call__(self, recorder: Recorder, workflow_path: str, templates: dict[str, str]):
        """
        Execute the workflow.

        Args:
            recorder: Recorder instance for logging.
            workflow_path: Path to the workflow configuration directory.
            templates: Dictionary of template values.

        Raises:
            Workflow.Exception: For workflow-specific errors.
        """
        pass
