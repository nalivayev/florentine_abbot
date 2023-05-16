from configparser import ConfigParser, ExtendedInterpolation
from argparse import ArgumentParser, Action
from solidol.log.log import log, Logger
from shutil import SameFileError, move
from solidol.image.exif import EXIF
from getpass import getuser
from subprocess import run
from pathlib import Path
from os import makedirs
from re import finditer
from typing import Any


class WorkflowParser(ArgumentParser):

    class KeyValueAction(Action):

        def __call__(self, p_parser, p_namespace, p_value, p_option=None):
            v_dictionary = {}
            if p_value:
                for v_pair in p_value:
                    v_key, v_value = v_pair.split("=")
                    v_dictionary[v_key] = v_value
            setattr(p_namespace, self.dest, v_dictionary)

    _required_group: Any

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(
            "-w",
            "--workflow",
            type=str,
            help="name of the workflow path"
        )
        self.add_argument(
            "-tl",
            "--template_list",
            type=str,
            nargs="+",
            action=WorkflowParser.KeyValueAction,
            help="list of templates"
        )

    def parse_args(self, p_args=None, p_namespace=None):
        v_result = ArgumentParser.parse_args(self, p_args, p_namespace)
        if not v_result.workflow:
            self.error("Incorrect name of the workflow path")
        return v_result


class VueScanWorkflow:

    class Exception(Exception):

        pass

    _WORKFLOW_SETTINGS_NAME = "workflow.ini"
    _VUESCAN_SETTINGS_NAME = "vuescan.ini"

    _logger: Logger
    _workflow_parser: ConfigParser
    _script_parser: ConfigParser
    _vuescan_parser: ConfigParser
    _workflow_path: Path
    _template_list: {}

    def _read_settings_file(self, p_path: Path) -> ConfigParser:
        if Path(p_path).exists():
            log(self._logger, [f"Loading settings from '{str(p_path)}'"])
            v_parser = ConfigParser(interpolation=ExtendedInterpolation())
            v_parser.read(p_path)
            log(self._logger, ["Settings loaded"])
            return v_parser
        else:
            raise VueScanWorkflow.Exception(f"Error loading settings from file '{p_path}'")

    # noinspection PyMethodMayBeStatic
    def _add_system_templates(self):
        self._template_list["user_name"] = getuser()

    def _read_settings(self):
        self._script_parser = self._read_settings_file(Path(__file__).with_suffix(".ini"))
        self._convert_templates_to_values(self._script_parser)
        v_workflow_settings_path_name = Path(self._workflow_path, self._WORKFLOW_SETTINGS_NAME)
        self._workflow_parser = self._read_settings_file(v_workflow_settings_path_name)
        log(self._logger, [f"Workflow description: {self._workflow_parser['main']['description']}"])
        self._vuescan_parser = self._read_settings_file(Path(self._workflow_path, self._VUESCAN_SETTINGS_NAME))

    def _merge_settings(self):
        for v_section in self._workflow_parser.sections():
            if v_section.startswith("vuescan."):
                v_vuescan_section = v_section.split(".")[-1]
                if not self._vuescan_parser.has_section(v_vuescan_section):
                    self._vuescan_parser.add_section(v_vuescan_section)
                v_items = self._workflow_parser.items(v_section)
                for v_item in v_items:
                    self._vuescan_parser[v_vuescan_section][v_item[0]] = v_item[1]
        log(self._logger, ["Merging workflow and VueScan settings was successful"])

    def _overwrite_vuescan_settings_file(self):
        v_path = Path(self._script_parser["main"]["settings_path"], self._script_parser["main"]["settings_name"])
        try:
            with open(v_path, 'w') as v_file:
                self._vuescan_parser.write(v_file)
        except (SameFileError, OSError):
            raise VueScanWorkflow.Exception("Error overwriting the VueScan settings file")
        log(self._logger, [f"VueScan settings file '{v_path}' overwritten"])

    def _run_vuescan(self):
        v_program_path_name = Path(
            self._script_parser["main"]["program_path"], self._script_parser["main"]["program_name"]
        )
        if v_program_path_name.exists():
            if not Path(self._workflow_parser["vuescan"]["output_path"]).exists():
                makedirs(self._workflow_parser["vuescan"]["output_path"], True)
            log(self._logger, [f"Launching VueScan from '{v_program_path_name}'"])
            run(
                f'cd /D "{self._script_parser["main"]["program_path"]}" & {self._script_parser["main"]["program_name"]}',
                shell=True
            )
            log(self._logger, ["VueScan is closed"])
        else:
            raise VueScanWorkflow.Exception(f"File '{v_program_path_name}' not found")

    # noinspection PyMethodMayBeStatic
    def _convert_value(self, p_value: str) -> str:
        v_fields = p_value.split(":")
        if len(v_fields) > 0:
            v_key = v_fields[0]
            try:
                v_value = self._template_list[v_key]
            except KeyError:
                raise VueScanWorkflow.Exception(f"Key {v_key} not found")
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
            except VueScanWorkflow.Exception as v_exception:
                log(self._logger, [str(v_exception)])
                continue
            v_result = v_result.replace(v_template, v_value)
        return v_result

    def _convert_templates_to_values(self, p_parser: ConfigParser):
        if p_parser:
            for v_section in p_parser.sections():
                for v_key, v_value in p_parser.items(v_section):
                    p_parser[v_section][v_key] = self._convert_template_to_value(v_value)

    def _add_output_file_templates(self, p_tags: {}) -> {}:
        v_value = p_tags.get(EXIF.EXIFIFD, {}).get("DateTimeDigitized", "")
        if v_value:
            try:
                v_datetime = EXIF.convert_value_to_datetime(v_value.decode())
            except EXIF.Exception:
                return
            for v_key in ["digitization_year", "digitization_month", "digitization_day", "digitization_hour",
                          "digitization_minute", "digitization_second"]:
                self._template_list[v_key] = getattr(v_datetime, v_key.replace("digitization_", ""), "")

    def _extract_exif_tags(self, p_path: Path) -> {}:
        try:
            return EXIF.extract(str(p_path))
        except EXIF.Exception as v_exception:
            log(self._logger, [str(v_exception)])
            log(self._logger, [f"Unable to extract EXIF from file '{p_path.name}'"])
            return {}

    def _move_output_file(self):
        v_input_path = Path(
            self._workflow_parser["vuescan"]["output_path"],
            f"{self._workflow_parser['vuescan']['output_file_name']}.{self._workflow_parser['vuescan']['output_extension_name']}"
        )
        if v_input_path.exists():
            self._add_output_file_templates(self._extract_exif_tags(v_input_path))
            self._convert_templates_to_values(self._workflow_parser)
            if not Path(self._workflow_parser["main"]["output_path"]).exists():
                makedirs(self._workflow_parser["main"]["output_path"], True)
            v_output_path = Path(
                self._workflow_parser["main"]["output_path"],
                f"{self._workflow_parser['main']['output_file_name']}{v_input_path.suffix}"
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
        v_input_path = Path(self._script_parser["main"]["logging_path"], self._script_parser["main"]["logging_name"])
        if v_input_path.exists():
            if not Path(self._workflow_parser["main"]["output_path"]).exists():
                makedirs(self._workflow_parser["main"]["output_path"], True)
            v_output_path = Path(
                self._workflow_parser["main"]["output_path"],
                f"{self._workflow_parser['main']['output_file_name']}{v_input_path.suffix}"
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

    def run(self, p_logger: Logger, p_workflow_path: str, p_template_list: {}):
        self._template_list = p_template_list
        self._logger = p_logger
        self._workflow_path = Path(p_workflow_path).resolve()
        log(self._logger, ["Starting the workflow"])
        self._add_system_templates()
        self._read_settings()
        self._merge_settings()
        self._overwrite_vuescan_settings_file()
        self._run_vuescan()
        self._move_output_file()
        self._move_logging_file()
        log(self._logger, ["Workflow completed successfully"])


def main():
    v_parser = WorkflowParser()
    v_args = v_parser.parse_args()
    v_workflow = VueScanWorkflow()
    v_logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    try:
        v_workflow.run(
            v_logger,
            getattr(v_args, "workflow", ""),
            getattr(v_args, "template_list", {})
        )
    except VueScanWorkflow.Exception as v_exception:
        log(v_logger, [str(v_exception)])


if __name__ == "__main__":
    main()
