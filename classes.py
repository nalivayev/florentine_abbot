from argparse import ArgumentParser, ArgumentError, ArgumentTypeError, Action
from configparser import ConfigParser, ExtendedInterpolation
from solidol.log.log import log, Logger
from shutil import SameFileError, move
from solidol.image.exif import EXIF
from datetime import datetime
from os.path import getmtime
from getpass import getuser
from subprocess import run
from pathlib import Path
from os import makedirs
from re import finditer
from typing import Any


class Arguments:

    class KeyValueAction(Action):

        def __call__(self, p_parser, p_namespace, p_value, p_option=None):
            v_dictionary = {}
            if p_value:
                for v_pair in p_value:
                    v_key, v_value = v_pair.split("=")
                    v_dictionary[v_key] = v_value
            setattr(p_namespace, self.dest, v_dictionary)

    @staticmethod
    def check_photo_size(p_value):
        try:
            v_value = float(p_value)
        except ValueError:
            raise ArgumentTypeError("Invalid photo side size value")
        if v_value <= 0:
            raise ArgumentError(None, "Invalid photo side size")
        return v_value

    @staticmethod
    def check_image_size(p_value):
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


class CalculatorParser(ArgumentParser):

    _required_group: Any

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.photo_width["keys"], **Arguments.photo_width["values"])
        self._required_group.add_argument(*Arguments.photo_height["keys"], **Arguments.photo_height["values"])
        self._required_group.add_argument(*Arguments.image_width["keys"], **Arguments.image_width["values"])
        self._required_group.add_argument(*Arguments.image_height["keys"], **Arguments.image_height["values"])
        self.add_argument(*Arguments.minimal_resolution["keys"], **Arguments.minimal_resolution["values"])
        self.add_argument(*Arguments.maximal_resolution["keys"], **Arguments.maximal_resolution["values"])
        self.add_argument(*Arguments.resolution_list["keys"], **Arguments.resolution_list["values"])


class WorkflowParser(ArgumentParser):

    _required_group: Any

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.workflow["keys"], **Arguments.workflow["values"])
        self.add_argument(*Arguments.template_list["keys"], **Arguments.template_list["values"])


class PathWorkflowParser(ArgumentParser):

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(*Arguments.workflow["keys"], **Arguments.workflow["values"])
        self._required_group.add_argument(*Arguments.folder["keys"], **Arguments.folder["values"])
        self.add_argument(*Arguments.pattern["keys"], **Arguments.pattern["values"])


class Calculator:

    def __call__(self, p_photo_width, p_photo_height, p_image_width, p_image_height, p_minimal_resolution, p_maximal_resolution, p_resolution_list) -> tuple:
        v_photo_width = max(p_photo_width, p_photo_height)
        v_photo_height = min(p_photo_width, p_photo_height)
        v_image_width = max(p_image_width, p_image_height)
        v_image_height = min(p_image_width, p_image_height)
        v_resolution_list = sorted(p_resolution_list) if p_resolution_list else []
        if p_minimal_resolution:
            if len(v_resolution_list) > 0:
                if v_resolution_list[0] > p_minimal_resolution:
                    v_minimal_resolution = v_resolution_list[0]
                else:
                    v_minimal_resolution = p_minimal_resolution
            else:
                v_minimal_resolution = p_minimal_resolution
        else:
            if len(v_resolution_list) > 0:
                v_minimal_resolution = v_resolution_list[0]
            else:
                v_minimal_resolution = None
        if p_maximal_resolution:
            if len(v_resolution_list) > 0:
                if v_resolution_list[len(v_resolution_list) - 1] < p_maximal_resolution:
                    v_maximal_resolution = v_resolution_list[len(v_resolution_list) - 1]
                else:
                    v_maximal_resolution = p_maximal_resolution
            else:
                v_maximal_resolution = p_maximal_resolution
        else:
            if len(v_resolution_list) > 0:
                v_maximal_resolution = v_resolution_list[len(v_resolution_list) - 1]
            else:
                v_maximal_resolution = None
        v_calculated_width_dpi = v_image_width / (v_photo_width / 2.54)
        v_calculated_height_dpi = v_image_height / (v_photo_height / 2.54)
        v_calculated_dpi = min(v_calculated_width_dpi, v_calculated_height_dpi)
        v_recommended_dpi = v_calculated_dpi
        for v_index, v_value in enumerate(v_resolution_list):
            if v_recommended_dpi < v_value:
                if v_index > 0 and v_value - v_recommended_dpi > v_recommended_dpi - v_resolution_list[v_index - 1]:
                    v_recommended_dpi = v_resolution_list[v_index - 1]
                else:
                    v_recommended_dpi = v_value
                break
        if v_minimal_resolution:
            v_recommended_dpi = max(v_minimal_resolution, v_recommended_dpi)
        if v_maximal_resolution:
            v_recommended_dpi = min(v_maximal_resolution, v_recommended_dpi)
        return v_calculated_dpi, v_recommended_dpi


class VueScanWorkflow:

    class Exception(Exception):

        pass

    _VUESCAN_SETTINGS_NAME = "vuescan.ini"
    _WORKFLOW_SETTINGS_NAME = "workflow.ini"

    _EXIF_TEMPLATE_NAMES = [
        "digitization_year",
        "digitization_month",
        "digitization_day",
        "digitization_hour",
        "digitization_minute",
        "digitization_second"
    ]

    _logger: Logger
    _workflow_parser: ConfigParser
    _script_parser: ConfigParser
    _workflow_path: Path
    _templates: {} = {}

    def _read_settings_file(self, p_path: Path) -> ConfigParser:
        if Path(p_path).exists():
            log(self._logger, [f"Loading settings from '{str(p_path)}'"])
            v_parser = ConfigParser(interpolation=ExtendedInterpolation())
            v_parser.read(p_path)
            log(self._logger, ["Settings loaded"])
            return v_parser
        else:
            raise VueScanWorkflow.Exception(f"Error loading settings from file '{p_path}'")

    def _add_system_templates(self):
        self._templates["user_name"] = getuser()

    def _read_settings(self):
        self._script_parser = self._read_settings_file(Path(Path(__file__).parent, self._VUESCAN_SETTINGS_NAME))
        self._workflow_parser = self._read_settings_file(Path(self._workflow_path, self._WORKFLOW_SETTINGS_NAME))
        log(self._logger, [f"Workflow description: {self._get_workflow_value('main', 'description')}"])

    def _get_workflow_value(self, p_section, p_key):
        v_value = self._workflow_parser[p_section][p_key]
        return self._convert_template_to_value(v_value)

    def _get_script_value(self, p_section, p_key):
        v_value = self._script_parser[p_section][p_key]
        return self._convert_template_to_value(v_value)

    def _overwrite_vuescan_settings_file(self):
        v_parser = ConfigParser()
        v_parser.add_section("VueScan")
        for v_section in self._workflow_parser.sections():
            if v_section.startswith("vuescan."):
                v_vuescan_section = v_section.split(".")[-1]
                if not v_parser.has_section(v_vuescan_section):
                    v_parser.add_section(v_vuescan_section)
                v_items = self._workflow_parser.items(v_section)
                for v_item in v_items:
                    v_parser[v_vuescan_section][v_item[0]] = self._get_workflow_value(v_section, v_item[0])
        v_path = Path(self._get_script_value("main", "settings_path"), self._get_script_value("main", "settings_name"))
        try:
            with open(v_path, "w") as v_file:
                v_parser.write(v_file)
        except (SameFileError, OSError):
            raise VueScanWorkflow.Exception("Error overwriting the VueScan settings file")
        log(self._logger, [f"VueScan settings file '{v_path}' overwritten"])

    def _run_vuescan(self):
        v_program_path = Path(
            self._get_script_value("main", "program_path"), self._get_script_value("main", "program_name")
        )
        if v_program_path.exists():
            v_output_path_name = self._get_workflow_value("vuescan", "output_path")
            if not Path(v_output_path_name).exists():
                makedirs(v_output_path_name, True)
            log(self._logger, [f"Launching VueScan from '{v_program_path}'"])
            run(
                f'cd /D "{self._get_script_value("main", "program_path")}" & {self._get_script_value("main", "program_name")}',
                shell=True
            )
            log(self._logger, ["VueScan is closed"])
        else:
            raise VueScanWorkflow.Exception(f"File '{v_program_path}' not found")

    def _convert_value(self, p_value: str) -> str:
        v_fields = p_value.split(":")
        if len(v_fields) > 0:
            v_key = v_fields[0]
            try:
                v_value = self._templates[v_key]
            except KeyError:
                raise VueScanWorkflow.Exception(f"Key '{v_key}' not found")
            try:
                v_length = int(v_fields[1]) if len(v_fields) > 1 else 0
                v_alignment = v_fields[2] if len(v_fields) > 2 and v_fields[2] in ("<", ">", "^") else "<"
                v_placeholder = v_fields[3] if len(v_fields) > 3 else ""
                v_result = f"{{:{v_placeholder}{v_alignment}{v_length}s}}"
                v_result = v_result.format(str(v_value))
                return v_result
            except ValueError:
                raise VueScanWorkflow.Exception("Template conversion error")
        else:
            raise VueScanWorkflow.Exception("An empty template was found")

    def _convert_template_to_value(self, p_template: str) -> str:
        v_result = p_template
        for v_match in finditer("{(.+?)}", p_template):
            v_template = p_template[v_match.start():v_match.end()]
            try:
                v_value = self._convert_value(v_template[1:-1])
            except VueScanWorkflow.Exception:
                log(self._logger, [f"Error converting template '{v_template[1:-1]}' to value"])
                continue
            v_result = v_result.replace(v_template, v_value)
        return v_result

    def _add_output_file_templates(self, p_path: Path) -> {}:
        v_datetime = None
        if p_path.suffix.lower() in [".tiff", ".tif", ".jpeg", ".jpg"]:
            v_tags = self._extract_exif_tags(p_path)
            v_value = v_tags.get(EXIF.EXIFIFD, {}).get("DateTimeDigitized", "")
            if v_value:
                try:
                    v_datetime = EXIF.convert_value_to_datetime(v_value.decode())
                except EXIF.Exception:
                    return
        else:
            v_datetime = datetime.fromtimestamp(getmtime(p_path))
        if v_datetime:
            for v_key in self._EXIF_TEMPLATE_NAMES:
                self._templates[v_key] = getattr(v_datetime, v_key.replace("digitization_", ""), "")

    def _extract_exif_tags(self, p_path: Path) -> {}:
        try:
            return EXIF.extract(str(p_path))
        except EXIF.Exception as v_exception:
            log(self._logger, [str(v_exception)])
            log(self._logger, [f"Unable to extract EXIF from file '{p_path.name}'"])
            return {}

    def _move_output_file(self):
        v_input_path = Path(
            self._get_workflow_value("vuescan", "output_path"),
            f"{self._get_workflow_value('vuescan', 'output_file_name')}.{self._get_workflow_value('vuescan', 'output_extension_name')}"
        )
        if v_input_path.exists():
            self._add_output_file_templates(v_input_path)
            v_output_path_name = self._get_workflow_value("main", "output_path")
            if not Path(v_output_path_name).exists():
                makedirs(v_output_path_name, True)
            v_output_path = Path(
                v_output_path_name,
                f"{self._get_workflow_value('main', 'output_file_name')}{v_input_path.suffix}"
            )
            try:
                move(v_input_path, v_output_path)
                log(self._logger, [
                    f"Scanned file '{v_input_path.name}' moved from '{v_input_path.parent}' to the '{v_output_path.parent}'",
                    f"The name of the final file is '{v_output_path.name}'"
                ])
            except OSError:
                raise VueScanWorkflow.Exception(
                    f"Error moving resulting file from '{v_input_path}' to '{v_output_path}'"
                )
        else:
            raise VueScanWorkflow.Exception(f"Output file '{v_input_path}' not found")

    def _move_logging_file(self):
        v_input_path = Path(
            self._get_script_value("main", "logging_path"), self._get_script_value("main", "logging_name")
        )
        if v_input_path.exists():
            v_output_path = Path(
                self._get_workflow_value("main", "output_path"),
                f"{self._get_workflow_value('main', 'output_file_name')}{v_input_path.suffix}"
            )
            try:
                move(v_input_path, v_output_path)
                log(self._logger, [
                    f"Logging file '{v_input_path.name}' moved from '{v_output_path.parent}' to the '{v_output_path.parent}'",
                    f"The name of the final file is '{v_output_path.name}'"
                ])
            except OSError:
                raise VueScanWorkflow.Exception(
                    f"Error moving resulting file from '{v_input_path}' to '{v_output_path}'"
                )
        else:
            log(self._logger, ["VueScan logging file not found"])

    def __call__(self, p_logger: Logger, p_workflow_path: str, p_templates: {}):
        self._templates = p_templates if p_templates else {}
        self._add_system_templates()
        self._logger = p_logger
        self._workflow_path = Path(p_workflow_path).resolve()
        log(self._logger, ["Starting the workflow"])
        self._read_settings()
        self._overwrite_vuescan_settings_file()
        self._run_vuescan()
        self._move_output_file()
        self._move_logging_file()
        log(self._logger, ["Workflow completed successfully"])
