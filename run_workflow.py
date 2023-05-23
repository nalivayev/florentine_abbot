from argparse import ArgumentParser, Action
from solidol.log.log import log, Logger
from pathlib import Path
from typing import Any
from workflow import VueScanWorkflow


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
        if not getattr(v_result, "workflow", None):
            self.error("Incorrect name of the workflow path")
        return v_result


def main():
    v_logger = Logger(str(Path(__file__).with_suffix(".log")), "workflow")
    v_parser = WorkflowParser()
    v_args = v_parser.parse_args()
    v_workflow = VueScanWorkflow()
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
