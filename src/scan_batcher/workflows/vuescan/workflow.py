from configparser import ConfigParser, ExtendedInterpolation
from shutil import SameFileError, move
from os.path import getmtime
from getpass import getuser
from subprocess import run
from pathlib import Path
from re import finditer
from os import makedirs
import datetime

from scan_batcher.recorder import log, Recorder
from scan_batcher.exifer import Exifer
from scan_batcher.workflows import register_workflow
from scan_batcher.workflow import Workflow


@register_workflow("vuescan")
class VuescanWorkflow(Workflow):
    """
    Workflow manager for VueScan scanning operations.

    Handles the complete workflow from configuration to file management
    for VueScan operations, including template processing and EXIF data handling.
    """

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

    def _read_settings_file(self, path: Path) -> ConfigParser:
        """
        Read and parse a configuration file.

        Args:
            path (Path): Path to the configuration file to read.

        Returns:
            ConfigParser: Instance with loaded configuration.

        Raises:
            Workflow.Exception: If the file cannot be read or doesn't exist.
        """
        if Path(path).exists():
            log(self._recorder, [f"Loading settings from '{str(path)}'"])
            parser = ConfigParser(interpolation=ExtendedInterpolation())
            parser.read(path)
            log(self._recorder, ["Settings loaded"])
            return parser
        else:
            raise VuescanWorkflow.Exception(f"Error loading settings from file '{path}'")

    def _add_system_templates(self):
        """
        Add system-provided templates (like current username) to the templates dictionary.
        """
        self._templates["user_name"] = getuser()

    def _read_settings(self):
        """
        Read both script and workflow configuration files and initialize parsers.
        """
        self._script_parser = self._read_settings_file(Path(Path(__file__).parent, self._VUESCAN_SETTINGS_NAME))
        self._workflow_parser = self._read_settings_file(Path(self._workflow_path, self._WORKFLOW_SETTINGS_NAME))
        log(self._recorder, [f"Workflow description: {self._get_workflow_value('main', 'description')}"])

    def _get_workflow_value(self, section, key):
        """
        Get a value from workflow configuration with template substitution.

        Args:
            section (str): Configuration section name.
            key (str): Key within the section.

        Returns:
            str: The configuration value with all templates resolved.
        """
        value = self._workflow_parser[section][key]
        return self._replace_templates_to_value(value)

    def _get_script_value(self, section, key):
        """
        Get a value from script configuration with template substitution.

        Args:
            section (str): Configuration section name.
            key (str): Key within the section.

        Returns:
            str: The configuration value with all templates resolved.
        """
        value = self._script_parser[section][key]
        return self._replace_templates_to_value(value)

    def _overwrite_vuescan_settings_file(self):
        """
        Generate and overwrite VueScan settings file based on workflow configuration.

        Raises:
            Workflow.Exception: If there's an error writing the file.
        """
        parser = ConfigParser()
        parser.add_section("VueScan")
        for section in self._workflow_parser.sections():
            if section.startswith("vuescan."):
                vuescan_section = section.split(".")[-1]
                if not parser.has_section(vuescan_section):
                    parser.add_section(vuescan_section)
                items = self._workflow_parser.items(section)
                for item in items:
                    parser[vuescan_section][item[0]] = self._get_workflow_value(section, item[0])
        path = Path(self._get_script_value("main", "settings_path"), self._get_script_value("main", "settings_name"))
        try:
            with open(path, "w") as file:
                parser.write(file)
        except (SameFileError, OSError):
            raise VuescanWorkflow.Exception("Error overwriting the VueScan settings file")
        log(self._recorder, [f"VueScan settings file '{path}' overwritten"])

    def _run_vuescan(self):
        """
        Execute the VueScan program with configured settings.

        Raises:
            Workflow.Exception: If VueScan executable is not found.
        """
        program_path = Path(
            self._get_script_value("main", "program_path"), self._get_script_value("main", "program_name")
        )
        if program_path.exists():
            output_path_name = self._get_workflow_value("vuescan", "output_path")
            if not Path(output_path_name).exists():
                makedirs(output_path_name, True)
            log(self._recorder, [f"Launching VueScan from '{program_path}'"])
            run(
                f'cd /D "{self._get_script_value("main", "program_path")}" & {self._get_script_value("main", "program_name")}',
                shell=True
            )
            log(self._recorder, ["VueScan is closed"])
        else:
            raise VuescanWorkflow.Exception(f"File '{program_path}' not found")

    def _convert_value(self, value: str) -> str:
        """
        Convert a template string to its actual value using the templates dictionary.

        Args:
            value (str): Template string to convert (e.g., "{key:length:alignment:placeholder}").

        Returns:
            str: Formatted string with the template replaced by its actual value.

        Raises:
            Workflow.Exception: If template is invalid or key not found.
        """
        fields = value.split(":")
        if len(fields) > 0:
            key = fields[0]
            try:
                value = self._templates[key]
            except KeyError:
                raise VuescanWorkflow.Exception(f"Key '{key}' not found")
            try:
                length = int(fields[1]) if len(fields) > 1 else 0
                alignment = fields[2] if len(fields) > 2 and fields[2] in ("<", ">", "^") else "<"
                placeholder = fields[3] if len(fields) > 3 else ""
                result = f"{{:{placeholder}{alignment}{length}s}}"
                result = result.format(str(value))
                return result
            except ValueError:
                raise VuescanWorkflow.Exception("Template conversion error")
        else:
            raise VuescanWorkflow.Exception("An empty template was found")

    def _replace_templates_to_value(self, string: str) -> str:
        """
        Replace all templates in a string with their corresponding values.

        Args:
            string (str): String containing template placeholders.

        Returns:
            str: String with all templates replaced by their values.
        """
        result = string
        for match in finditer("{(.+?)}", string):
            template = string[match.start():match.end()]
            try:
                value = self._convert_value(template[1:-1])
            except VuescanWorkflow.Exception:
                log(self._recorder, [f"Error converting template '{string[1:-1]}' to value"])
                continue
            result = result.replace(template, value)
        return result

    def _add_output_file_templates(self, path: Path) -> dict[str, str]:
        """
        Extract EXIF data from scanned file and add datetime templates.

        Args:
            path (Path): Path to the scanned file.
        """
        moment = None
        if path.suffix.lower() in [".tiff", ".tif", ".jpeg", ".jpg"]:
            tags = self._extract_exif_tags(path)
            value = tags.get(Exifer.EXIFIFD, {}).get("DateTimeDigitized", "")
            if value:
                try:
                    moment = Exifer.convert_value_to_datetime(value.decode())
                except Exifer.Exception:
                    return
        else:
            moment = datetime.datetime.fromtimestamp(getmtime(path))
        if moment:
            for key in self._EXIF_TEMPLATE_NAMES:
                self._templates[key] = getattr(moment, key.replace("digitization_", ""), "")

    def _extract_exif_tags(self, path: Path) -> dict[str, str]:
        """
        Extract EXIF metadata from an image file.

        Args:
            path (Path): Path to the image file.

        Returns:
            dict: Dictionary of EXIF tags or empty dict if extraction fails.
        """
        try:
            return Exifer.extract(str(path))
        except Exifer.Exception as e:
            log(self._recorder, [str(e)])
            log(self._recorder, [f"Unable to extract EXIF from file '{path.name}'"])
            return {}

    def _move_output_file(self):
        """
        Move the scanned file from VueScan output to final destination.

        Raises:
            Workflow.Exception: If output file not found or move fails.
        """
        input_path = Path(
            self._get_workflow_value("vuescan", "output_path"),
            f"{self._get_workflow_value('vuescan', 'output_file_name')}.{self._get_workflow_value('vuescan', 'output_extension_name')}"
        )
        if input_path.exists():
            self._add_output_file_templates(input_path)
            output_path_name = self._get_workflow_value("main", "output_path")
            if not Path(output_path_name).exists():
                makedirs(output_path_name, True)
            output_path = Path(
                output_path_name,
                f"{self._get_workflow_value('main', 'output_file_name')}{input_path.suffix}"
            )
            try:
                move(input_path, output_path)
                log(self._recorder, [
                    f"Scanned file '{input_path.name}' moved from '{input_path.parent}' to the '{output_path.parent}'",
                    f"The name of the final file is '{output_path.name}'"
                ])
            except OSError:
                raise VuescanWorkflow.Exception(
                    f"Error moving resulting file from '{input_path}' to '{output_path}'"
                )
        else:
            raise VuescanWorkflow.Exception(f"Output file '{input_path}' not found")

    def _move_logging_file(self):
        """
        Move VueScan log file to the output directory.
        """
        input_path = Path(
            self._get_script_value("main", "logging_path"), self._get_script_value("main", "logging_name")
        )
        if input_path.exists():
            output_path = Path(
                self._get_workflow_value("main", "output_path"),
                f"{self._get_workflow_value('main', 'output_file_name')}{input_path.suffix}"
            )
            try:
                move(input_path, output_path)
                log(self._recorder, [
                    f"Logging file '{input_path.name}' moved from '{output_path.parent}' to the '{output_path.parent}'",
                    f"The name of the final file is '{output_path.name}'"
                ])
            except OSError:
                raise VuescanWorkflow.Exception(
                    f"Error moving resulting file from '{input_path}' to '{output_path}'"
                )
        else:
            log(self._recorder, ["VueScan logging file not found"])

    def __call__(self, recorder: Recorder, workflow_path: str, templates: dict[str, str]):
        """
        Execute the complete VueScan workflow.

        Args:
            recorder (Recorder): Recorder instance for recording workflow progress.
            workflow_path (str): Path to the workflow configuration directory.
            templates (dict[str, str]): Dictionary of initial template values.
        """
        self._templates = templates if templates else {}
        self._add_system_templates()
        self._recorder = recorder
        self._workflow_path = Path(workflow_path).resolve()
        log(self._recorder, ["Starting the workflow"])
        self._read_settings()
        self._overwrite_vuescan_settings_file()
        self._run_vuescan()
        self._move_output_file()
        self._move_logging_file()
        log(self._recorder, ["Workflow completed successfully"])
