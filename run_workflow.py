from classes import WorkflowParser, VueScanWorkflow
from solidol.log.log import log, Logger
from pathlib import Path


def main():
    v_logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    v_parser = WorkflowParser()
    v_args = v_parser.parse_args()
    v_workflow = VueScanWorkflow()
    try:
        v_workflow(
            v_logger,
            getattr(v_args, "workflow", ""),
            getattr(v_args, "template_list", {})
        )
    except VueScanWorkflow.Exception as v_exception:
        log(v_logger, [str(v_exception)])


if __name__ == "__main__":
    main()
