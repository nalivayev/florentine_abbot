from sys import stderr, exit
from typing import List
from pathlib import Path

from scan_batcher.recorder import log, Recorder
from scan_batcher.batch import Batch, Scan
from scan_batcher.parser import Parser
from scan_batcher.workflows import get_workflow


def get_subclasses(cls):
    """
    Recursively find all subclasses of a given class, including subclasses of subclasses.

    Args:
        cls (type): The base class to search subclasses for.

    Returns:
        list: List of all subclasses (including nested).
    """
    subclasses = []
    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_subclasses(subclass))
    return subclasses

def create_batch(recorder: Recorder, batch: List, min_res: int, max_res: int, res_list, rounding) -> Batch:
    """
    Create a Batch subclass instance based on the input batch type (case-insensitive).
    Supports all direct and indirect subclasses of Batch.

    Args:
        recorder (Recorder): Recorder instance for logging.
        batch (List): List where the first element specifies the batch type (e.g., "Scan", "CALCULATE").
        min_res (int): Minimum resolution parameter for the batch.
        max_res (int): Maximum resolution parameter for the batch.
        res_list: List of resolutions for processing.
        rounding: Rounding method to apply.

    Returns:
        Batch: An instance of the matching Batch subclass (e.g., Scan, Calculate, Process).

    Raises:
        ValueError: If the batch type is unknown or empty (defaults to Scan if batch is empty/None).
    """
    if not batch or batch[0] == "":
        return Scan(recorder, min_res, max_res, res_list, rounding, *batch[1:])
    
    kind = batch[0].lower()  # Case-insensitive comparison
    
    # Search through all subclasses (including nested)
    for cls in get_subclasses(Batch):
        if cls.__name__.lower() == kind:
            return cls(recorder, min_res, max_res, res_list, rounding, *batch[1:])
    
    raise ValueError(f"Unknown batch type: {batch[0]}")

def create_workflow(engine: str = "vuescan"):
    """
    Get a registered workflow class by engine name and return its instance.

    Args:
        engine (str): The type of engine to create (e.g., "vuescan", "silverfast").

    Returns:
        Workflow: An instance of the Workflow class.

    Raises:
        ValueError: If the workflow is not registered.
    """
    workflow_class = get_workflow(engine)
    return workflow_class()

def main():
    """
    Main entry point for the CLI utility.

    Initializes logging, parses arguments, creates batch and workflow objects,
    and executes the workflow for each batch item.
    """
    recorder = Recorder(str(Path(__file__).with_suffix(".log")), "workflow")
    log(recorder, ["Script has been started"])
    parser = Parser()
    args = parser.parse_args()
    batch = create_batch(recorder, args.batch, args.min_dpi, args.max_dpi, args.dpis, args.rounding)

    workflow = create_workflow(args.engine)
    for item in batch:
        try:
            batch_dict = dict(item) if isinstance(item, list) else item
            templates_dict = dict(args.templates) if args.templates else {}

            if batch_dict:
                merged_templates = {**templates_dict, **batch_dict}
            else:
                merged_templates = {**templates_dict}
            workflow(recorder, args.workflow, merged_templates)

        except KeyboardInterrupt:
            log(recorder, ["\nExiting..."])
            exit(0)
        except Exception as e:
            print(f"\nError: {e}", file=stderr)
            continue

    log(recorder, ["Script has been completed"])

if __name__ == "__main__":
    main()
