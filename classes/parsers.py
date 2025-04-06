from argparse import ArgumentParser, _ArgumentGroup
from .arguments import Arguments

class CalculatorParser(ArgumentParser):
    """
    A command-line argument parser for image calculation parameters.
    
    This parser handles arguments related to image dimensions, resolutions, 
    and rounding settings. It groups required arguments separately for better 
    user interface.

    Attributes:
        _required_group (argparse._ArgumentGroup): Argument group containing 
            all required parameters.
    """

    _required_group: _ArgumentGroup

    def __init__(self):
        """Initialize the CalculatorParser with all image calculation arguments."""
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.photo_width["keys"], **Arguments.photo_width["values"])
        self._required_group.add_argument(*Arguments.photo_height["keys"], **Arguments.photo_height["values"])
        self._required_group.add_argument(*Arguments.image_width["keys"], **Arguments.image_width["values"])
        self._required_group.add_argument(*Arguments.image_height["keys"], **Arguments.image_height["values"])
        self.add_argument(*Arguments.minimal_resolution["keys"], **Arguments.minimal_resolution["values"])
        self.add_argument(*Arguments.maximal_resolution["keys"], **Arguments.maximal_resolution["values"])
        self.add_argument(*Arguments.resolution_list["keys"], **Arguments.resolution_list["values"])
        self.add_argument(*Arguments.rounding["keys"], **Arguments.rounding["values"])

class WorkflowParser(ArgumentParser):
    """
    A command-line argument parser for workflow selection.
    
    Handles the basic workflow arguments including the main workflow selection
    and optional template specifications.

    Attributes:
        _required_group (argparse._ArgumentGroup): Argument group containing 
            the required workflow parameter.
    """

    _required_group: _ArgumentGroup

    def __init__(self):
        """Initialize the WorkflowParser with workflow-related arguments."""
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.workflow["keys"], **Arguments.workflow["values"])
        self.add_argument(*Arguments.template_list["keys"], **Arguments.template_list["values"])


class PathWorkflowParser(ArgumentParser):
    """
    An extended workflow parser that includes path-related arguments.
    
    Builds upon WorkflowParser by adding folder and pattern arguments for
    file system operations.

    Attributes:
        _required_group (argparse._ArgumentGroup): Argument group containing 
            required workflow and folder parameters.
    """

    def __init__(self):
        """Initialize the PathWorkflowParser with path and workflow arguments."""
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.workflow["keys"], **Arguments.workflow["values"])
        self._required_group.add_argument(*Arguments.folder["keys"], **Arguments.folder["values"])
        self.add_argument(*Arguments.pattern["keys"], **Arguments.pattern["values"])
