from configparser import ConfigParser, ExtendedInterpolation
from solidol.log.log import log, Logger
from shutil import SameFileError, move
from solidol.image.exif import EXIF
from datetime import datetime
from os.path import getmtime
from getpass import getuser
from subprocess import run
from pathlib import Path
from re import finditer
from os import makedirs

class VueScanWorkflow:
    """A workflow manager for VueScan scanning operations.
    
    This class handles the complete workflow from configuration to file management
    for VueScan operations, including template processing and EXIF data handling.
    """

    class Exception(Exception):
        """Custom exception class for VueScan workflow errors."""
        pass

    def _read_settings_file(self, path: Path) -> ConfigParser:
        """Read and parse a configuration file.

        Args:
            path: Path to the configuration file to read.

        Returns:
            ConfigParser instance with loaded configuration.

        Raises:
            VueScanWorkflow.Exception: If the file cannot be read or doesn't exist.
        """
        if Path(path).exists():
            log(self._logger, [f"Loading settings from '{str(path)}'"])
            parser = ConfigParser(interpolation=ExtendedInterpolation())
            parser.read(path)
            log(self._logger, ["Settings loaded"])
            return parser
        else:
            raise VueScanWorkflow.Exception(f"Error loading settings from file '{path}'")

    def _add_system_templates(self):
        """Add system-provided templates (like current username) to the templates dictionary."""
        self._templates["user_name"] = getuser()

    def _read_settings(self):
        """Read both script and workflow configuration files and initialize parsers."""
        self._script_parser = self._read_settings_file(Path(Path(__file__).parent, self._VUESCAN_SETTINGS_NAME))
        self._workflow_parser = self._read_settings_file(Path(self._workflow_path, self._WORKFLOW_SETTINGS_NAME))
        log(self._logger, [f"Workflow description: {self._get_workflow_value('main', 'description')}"])

    def _get_workflow_value(self, section, key):
        """Get a value from workflow configuration with template substitution.

        Args:
            section: Configuration section name.
            key: Key within the section.

        Returns:
            The configuration value with all templates resolved.
        """
        value = self._workflow_parser[section][key]
        return self._convert_template_to_value(value)

    def _get_script_value(self, section, key):
        """Get a value from script configuration with template substitution.

        Args:
            section: Configuration section name.
            key: Key within the section.

        Returns:
            The configuration value with all templates resolved.
        """
        value = self._script_parser[section][key]
        return self._convert_template_to_value(value)

    def _overwrite_vuescan_settings_file(self):
        """Generate and overwrite VueScan settings file based on workflow configuration.

        Raises:
            VueScanWorkflow.Exception: If there's an error writing the file.
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
            raise VueScanWorkflow.Exception("Error overwriting the VueScan settings file")
        log(self._logger, [f"VueScan settings file '{path}' overwritten"])

    def _run_vuescan(self):
        """Execute the VueScan program with configured settings.

        Raises:
            VueScanWorkflow.Exception: If VueScan executable is not found.
        """
        program_path = Path(
            self._get_script_value("main", "program_path"), self._get_script_value("main", "program_name")
        )
        if program_path.exists():
            output_path_name = self._get_workflow_value("vuescan", "output_path")
            if not Path(output_path_name).exists():
                makedirs(output_path_name, True)
            log(self._logger, [f"Launching VueScan from '{program_path}'"])
            run(
                f'cd /D "{self._get_script_value("main", "program_path")}" & {self._get_script_value("main", "program_name")}',
                shell=True
            )
            log(self._logger, ["VueScan is closed"])
        else:
            raise VueScanWorkflow.Exception(f"File '{program_path}' not found")

    def _convert_value(self, value: str) -> str:
        """Convert a template string to its actual value using the templates dictionary.

        Args:
            value: Template string to convert (e.g., "{key:length:alignment:placeholder}").

        Returns:
            Formatted string with the template replaced by its actual value.

        Raises:
            VueScanWorkflow.Exception: If template is invalid or key not found.
        """
        fields = value.split(":")
        if len(fields) > 0:
            key = fields[0]
            try:
                value = self._templates[key]
            except KeyError:
                raise VueScanWorkflow.Exception(f"Key '{key}' not found")
            try:
                length = int(fields[1]) if len(fields) > 1 else 0
                alignment = fields[2] if len(fields) > 2 and fields[2] in ("<", ">", "^") else "<"
                placeholder = fields[3] if len(fields) > 3 else ""
                result = f"{{:{placeholder}{alignment}{length}s}}"
                result = result.format(str(value))
                return result
            except ValueError:
                raise VueScanWorkflow.Exception("Template conversion error")
        else:
            raise VueScanWorkflow.Exception("An empty template was found")

    def _convert_template_to_value(self, template: str) -> str:
        """Replace all templates in a string with their corresponding values.

        Args:
            template: String containing template placeholders.

        Returns:
            String with all templates replaced by their values.
        """
        result = template
        for match in finditer("{(.+?)}", template):
            template = template[match.start():match.end()]
            try:
                value = self._convert_value(template[1:-1])
            except VueScanWorkflow.Exception:
                log(self._logger, [f"Error converting template '{template[1:-1]}' to value"])
                continue
            result = result.replace(template, value)
        return result

    def _add_output_file_templates(self, path: Path) -> dict[str, str]:
        """Extract EXIF data from scanned file and add datetime templates.

        Args:
            path: Path to the scanned file.
        """
        datetime = None
        if path.suffix.lower() in [".tiff", ".tif", ".jpeg", ".jpg"]:
            tags = self._extract_exif_tags(path)
            value = tags.get(EXIF.EXIFIFD, {}).get("DateTimeDigitized", "")
            if value:
                try:
                    datetime = EXIF.convert_value_to_datetime(value.decode())
                except EXIF.Exception:
                    return
        else:
            datetime = datetime.fromtimestamp(getmtime(path))
        if datetime:
            for key in self._EXIF_TEMPLATE_NAMES:
                self._templates[key] = getattr(datetime, key.replace("digitization_", ""), "")

    def _extract_exif_tags(self, path: Path) -> dict[str, str]:
        """Extract EXIF metadata from an image file.

        Args:
            path: Path to the image file.

        Returns:
            Dictionary of EXIF tags or empty dict if extraction fails.
        """
        try:
            return EXIF.extract(str(path))
        except EXIF.Exception as e:
            log(self._logger, [str(e)])
            log(self._logger, [f"Unable to extract EXIF from file '{path.name}'"])
            return {}

    def _move_output_file(self):
        """Move the scanned file from VueScan output to final destination.

        Raises:
            VueScanWorkflow.Exception: If output file not found or move fails.
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
                log(self._logger, [
                    f"Scanned file '{input_path.name}' moved from '{input_path.parent}' to the '{output_path.parent}'",
                    f"The name of the final file is '{output_path.name}'"
                ])
            except OSError:
                raise VueScanWorkflow.Exception(
                    f"Error moving resulting file from '{input_path}' to '{output_path}'"
                )
        else:
            raise VueScanWorkflow.Exception(f"Output file '{input_path}' not found")

    def _move_logging_file(self):
        """Move VueScan log file to the output directory."""
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
                log(self._logger, [
                    f"Logging file '{input_path.name}' moved from '{output_path.parent}' to the '{output_path.parent}'",
                    f"The name of the final file is '{output_path.name}'"
                ])
            except OSError:
                raise VueScanWorkflow.Exception(
                    f"Error moving resulting file from '{input_path}' to '{output_path}'"
                )
        else:
            log(self._logger, ["VueScan logging file not found"])

    def __call__(self, logger: Logger, workflow_path: str, templates: dict[str, str]):
        """Execute the complete VueScan workflow.

        Args:
            logger: Logger instance for recording workflow progress.
            workflow_path: Path to the workflow configuration directory.
            templates: Dictionary of initial template values.
        """
        self._templates = templates if templates else {}
        self._add_system_templates()
        self._logger = logger
        self._workflow_path = Path(workflow_path).resolve()
        log(self._logger, ["Starting the workflow"])
        self._read_settings()
        self._overwrite_vuescan_settings_file()
        self._run_vuescan()
        self._move_output_file()
        self._move_logging_file()
        log(self._logger, ["Workflow completed successfully"])
