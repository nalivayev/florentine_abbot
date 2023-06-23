from argparse import ArgumentParser
from solidol.log.log import log, Logger
from pathlib import Path
from workflow import VueScanWorkflow


class PathWorkflowParser(ArgumentParser):

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(
            "-w",
            "--workflow",
            type=str,
            help="name of the workflow path"
        )
        self._required_group.add_argument(
            "-f",
            "--folder",
            type=str,
            help="name of the folder with files to process"
        )
        self.add_argument(
            "-p",
            "--pattern",
            type=str,
            help="files selection pattern, e.g. '*.tiff'",
            default="*.*"
        )

    def parse_args(self, p_args=None, p_namespace=None):
        v_result = ArgumentParser.parse_args(self, p_args, p_namespace)
        if not getattr(v_result, "workflow", None):
            self.error("Incorrect name of the workflow path")
        if not getattr(v_result, "folder", None):
            self.error("Incorrect name of the folder")
        return v_result


def main():
    v_logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    v_parser = PathWorkflowParser()
    v_args = v_parser.parse_args()
    v_folder = getattr(v_args, "folder", "")
    v_folder = Path(v_folder).resolve() if v_folder else Path("").resolve()
    v_pattern = getattr(v_args, "pattern", "*.*")
    v_pattern = v_pattern if v_pattern else "*.*"
    v_workflow_path = getattr(v_args, "workflow", "")
    v_files = Path(v_folder).glob(v_pattern)
    v_workflow = VueScanWorkflow()
    log(v_logger, [f"Start of folder processing '{v_folder}'"])
    v_count = 0
    if v_files:
        for v_file in v_files:
            try:
                log(v_logger, ["\n"])
                log(v_logger, ["\n"])
                log(v_logger, ["\n"])
                v_workflow.run(v_logger, v_workflow_path, {"source_filename": v_file})
                v_count += 1
            except VueScanWorkflow.Exception as v_exception:
                log(v_logger, [str(v_exception)])
    if not v_count:
        log(v_logger, [f"Files matching the specified filter were not found in the folder '{v_folder}'"])
    log(v_logger, [f"Folder processing '{v_folder}' completed"])


if __name__ == "__main__":
    main()
