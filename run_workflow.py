from classes.parsers import WorkflowParser
from classes.workflow import VueScanWorkflow
from solidol.log.log import log, Logger
from pathlib import Path


def main():
    logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    parser = WorkflowParser()
    args = parser.parse_args()
    workflow = VueScanWorkflow()
    try:
        workflow(
            logger,
            getattr(args, "workflow", ""),
            getattr(args, "template_list", {})
        )
    except VueScanWorkflow.Exception as e:
        log(logger, [str(e)])


if __name__ == "__main__":
    main()
