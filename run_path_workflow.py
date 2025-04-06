from classes.parsers import PathWorkflowParser
from classes.VueScan.workflow import VueScanWorkflow
from solidol.log.log import log, Logger
from pathlib import Path


def main():
    """Main function that processes files using VueScan workflow.
    
    The function performs the following steps:
    1. Initializes logging system
    2. Parses command line arguments
    3. Searches for files matching specified pattern
    4. Processes each file through VueScan workflow
    5. Handles errors and logs processing results
    
    Command line arguments:
        --folder: Directory to process (default: current directory)
        --pattern: File pattern to match (default: '*.*')
        --workflow: Path to custom workflow configuration (optional)
    """
    logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    parser = PathWorkflowParser()
    args = parser.parse_args()
    folder = getattr(args, "folder", "")
    folder = Path(folder).resolve() if folder else Path("").resolve()
    pattern = getattr(args, "pattern", "*.*")
    pattern = pattern if pattern else "*.*"
    workflow_path = getattr(args, "workflow", "")
    files = Path(folder).glob(pattern)
    workflow = VueScanWorkflow()
    log(logger, [f"Start of folder processing '{folder}'"])
    v_count = 0
    if files:
        for file in files:
            try:
                log(logger, ["\n\n\n"])
                workflow(logger, workflow_path, {"source_filename": file})
                v_count += 1
            except VueScanWorkflow.Exception as v_exception:
                log(logger, [str(v_exception)])
    if not v_count:
        log(logger, [f"Files matching the specified filter were not found in the folder '{folder}'"])
    log(logger, [f"Folder processing '{folder}' completed"])


if __name__ == "__main__":
    """Entry point when script is executed directly.
    
    Calls the main function to start file processing workflow.
    """
    main()
