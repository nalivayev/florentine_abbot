from argparse import ArgumentParser, ArgumentError, ArgumentTypeError, Action

class Arguments:
    """
    A class that defines and manages command-line arguments for the application.
    
    This class contains argument definitions and validation methods for various parameters
    including photo dimensions, image dimensions, resolution settings, and file processing options.
    """
    
    class KeyValueAction(Action):
        """
        A custom action class for parsing key-value pairs from command-line arguments.
        
        This action converts input strings in format 'key=value' into dictionary entries
        and stores them in the namespace.
        """
        def __call__(self, p_parser, p_namespace, p_value, p_option=None):
            v_dictionary = {}
            if p_value:
                for v_pair in p_value:
                    v_key, v_value = v_pair.split("=")
                    v_dictionary[v_key] = v_value
            setattr(p_namespace, self.dest, v_dictionary)

    @staticmethod
    def check_photo_size(p_value):
        """
        Validate and convert photo dimension input.
        
        Args:
            p_value: Input value to validate as a photo dimension
            
        Returns:
            float: Validated photo dimension value
            
        Raises:
            ArgumentTypeError: If value cannot be converted to float
            ArgumentError: If value is not positive
        """
        try:
            v_value = float(p_value)
        except ValueError:
            raise ArgumentTypeError("Invalid photo side size value")
        if v_value <= 0:
            raise ArgumentError(None, "Invalid photo side size")
        return v_value

    @staticmethod
    def check_image_size(p_value):
        """
        Validate and convert image dimension input.
        
        Args:
            p_value: Input value to validate as an image dimension
            
        Returns:
            int: Validated image dimension value
            
        Raises:
            ArgumentTypeError: If value cannot be converted to integer
            ArgumentError: If value is not positive
        """
        try:
            v_value = int(p_value)
        except ValueError:
            raise ArgumentTypeError("Invalid digitized image side size value")
        if v_value <= 0:
            raise ArgumentError(None, "Invalid digitized image side size")
        return v_value

    photo_width = {
        "keys": ["-pw", "--photo-width"],
        "values": {
            "type": check_photo_size,
            "help": "width of a photograph or picture in centimeters"
        }
    }
    photo_height = {
        "keys": ["-ph", "--photo-height"],
        "values": {
            "type": check_photo_size,
            "help": "height of a photograph or picture in centimeters"
        }
    }
    image_width = {
        "keys": ["-iw", "--image-width"],
        "values": {
            "type": check_image_size,
            "help": "desired width of the digitized image in pixels"
        }
    }
    image_height = {
        "keys": ["-ih", "--image-height"],
        "values": {
            "type": check_image_size,
            "help": "desired height of the digitized image in pixels"
        }
    }
    minimal_resolution = {
        "keys": ["-mnr", "--minimal-resolution"],
        "values": {"type": int, "help": "minimum resolution when scanning in DPI"}
    }
    maximal_resolution = {
        "keys": ["-mxr", "--maximal-resolution"],
        "values": {"type": int, "help": "maximal resolution when scanning in DPI"}
    }
    resolution_list = {
        "keys": ["-rl", "--resolution-list"],
        "values": {
            "type": int,
            "nargs": "+",
            "help": "a list of DPI resolutions supported by the scanner, separated by comma, e.g., '100, 300, 1200'"
        }
    }
    workflow = {
        "keys": ["-w", "--workflow"],
        "values": {"type": str, "help": "name of the workflow path", "required": True}
    }
    template_list = {
        "keys": ["-tl", "--template-list"],
        "values": {"type": str, "nargs": "+", "action": KeyValueAction, "help": "list of templates"}
    }
    folder = {
        "keys": ["-f", "--folder"],
        "values": {"type": str, "help": "name of the folder with files to process"}
    }
    pattern = {
        "keys": ["-p", "--pattern"],
        "values": {"type": str, "default": "*.*", "help": "files selection pattern, e.g. '*.tiff'"}
    }
    rounding = {
        "keys": ["-rnd", "--rounding"],
        "values": {
            "choices": ["mx", "mn", "nr"],
            "default": "nr",
            "help": "how to round the calculated resolution value"
        }
    }
