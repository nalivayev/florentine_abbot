from argparse import ArgumentParser, ArgumentError, ArgumentTypeError, Action


class KeyValueAction(Action):
    """
    Custom argparse action to parse key-value pairs from command-line arguments.

    Converts input strings in the format 'key=value' into dictionary entries
    and stores them in the namespace.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        """
        Parse key-value pairs and store as a dictionary in the namespace.

        Args:
            parser (ArgumentParser): The parser instance.
            namespace (Namespace): The namespace to update.
            value (list): List of key=value strings.
            option_string (str, optional): The option string seen on the command line.
        """
        dictionary = {}
        if value:
            for pair in value:
                key, value = pair.split("=")
                dictionary[key] = value
        setattr(namespace, self.dest, dictionary)


class Arguments:
    """
    Defines and manages command-line arguments for the application.

    Contains argument definitions and validation methods for parameters
    including photo dimensions, image dimensions, resolution settings, and file processing options.
    """

    @staticmethod
    def check_photo_size(value):
        """
        Validate and convert photo dimension input.

        Args:
            value: Input value to validate as a photo dimension.

        Returns:
            float: Validated photo dimension value.

        Raises:
            ArgumentTypeError: If value cannot be converted to float.
            ArgumentError: If value is not positive.
        """
        try:
            value = float(value)
        except ValueError:
            raise ArgumentTypeError("Invalid photo side size value")
        if value <= 0:
            raise ArgumentError(None, "Invalid photo side size")
        return value

    @staticmethod
    def check_image_size(value):
        """
        Validate and convert image dimension input.

        Args:
            value: Input value to validate as an image dimension.

        Returns:
            int: Validated image dimension value.

        Raises:
            ArgumentTypeError: If value cannot be converted to integer.
            ArgumentError: If value is not positive.
        """
        try:
            value = int(value)
        except ValueError:
            raise ArgumentTypeError("Invalid digitized image side size value")
        if value <= 0:
            raise ArgumentError(None, "Invalid digitized image side size")
        return value

    workflow = {
        "keys": ["-w", "--workflow"],
        "values": {
            "type": str, 
            "help": "Path to the workflow configuration file (INI format) for batch processing"
        }
    }

    templates = {
        "keys": ["-t", "--templates"],
        "values": {
            "type": str, 
            "nargs": "+", 
            "action": KeyValueAction, 
            "help": "List of template key-value pairs for file naming or metadata, e.g. -t year=2024 author=Smith"
        }
    }

    engine = {
        "keys": ["-e", "--engine"],
        "values": {
            "type": str, 
            "default": "vuescan", 
            "help": "Scan engine to use for processing (default: vuescan)"
        }
    }
    
    batch = {
        "keys": ["-b", "--batch"],
        "values": {
            "default": ["scan"],
            "nargs": '+',
            "help": "Batch mode: scan (interactive), calculate (single calculation), or process (folder processing). Default: scan"
        }
    }
    
    photo_min_side = {
        "keys": ["-ps", "--photo-min-side"],
        "values": {
            "type": check_photo_size,
            "required": True,
            "help": "Minimum length of the photo's shorter side (in centimeters, must be > 0)"
        }
    }

    image_min_side = {
        "keys": ["-is", "--image-min-side"],
        "values": {
            "type": int,
            "required": True,
            "help": "Minimum length of the image's shorter side (in pixels, must be > 0)"
        }
    }

    min_dpi = {
        "keys": ["-mnd", "--min-dpi"],
        "values": {
            "type": int, 
            "help": "Minimum allowed DPI value for scanning (optional)"
        }
    }

    max_dpi = {
        "keys": ["-mxd", "--max-dpi"],
        "values": {
            "type": int, 
            "help": "Maximum allowed DPI value for scanning (optional)"
        }
    }

    dpis = {
        "keys": ["-d", "--dpis"],
        "values": {
            "type": int,
            "nargs": "+",
            "help": "List of supported DPI resolutions by the scanner, separated by space, e.g., 100 300 1200"
        }
    }

    rounding = {
        "keys": ["-rd", "--rounding"],
        "values": {
            "choices": ["mx", "mn", "nr"],
            "default": "nr",
            "help": "Rounding strategy for calculated DPI: mx (maximum), mn (minimum), nr (nearest). Default: nr"
        }
    }


class Parser(ArgumentParser):
    """
    Command-line argument parser for image calculation parameters.

    Handles arguments related to image dimensions, resolutions, 
    and rounding settings. Groups required arguments separately for better 
    user interface.
    """

    def __init__(self):
        """
        Initialize the Parser with all image calculation arguments.
        """
        ArgumentParser.__init__(self)
        # Group required arguments for better help output
        required_group = self.add_argument_group("required arguments")
        # Add all arguments to the parser
        self.add_argument(*Arguments.batch["keys"], **Arguments.batch["values"])
        self.add_argument(*Arguments.workflow["keys"], **Arguments.workflow["values"])
        self.add_argument(*Arguments.templates["keys"], **Arguments.templates["values"])
        self.add_argument(*Arguments.engine["keys"], **Arguments.engine["values"])
        self.add_argument(*Arguments.min_dpi["keys"], **Arguments.min_dpi["values"])
        self.add_argument(*Arguments.max_dpi["keys"], **Arguments.max_dpi["values"])
        self.add_argument(*Arguments.dpis["keys"], **Arguments.dpis["values"])
        self.add_argument(*Arguments.rounding["keys"], **Arguments.rounding["values"])
