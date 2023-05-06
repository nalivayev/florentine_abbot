import logging


class Logger:

    _logger: logging.Logger

    def __init__(self, p_path: str, p_category: str):
        self._logger = logging.getLogger(p_category)
        self._logger.setLevel(logging.INFO)
        v_formatter = logging.Formatter("%(asctime)s.%(msecs)03d %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
        v_handler = logging.FileHandler(f"{p_path}", mode="w")
        v_handler.setFormatter(v_formatter)
        self._logger.addHandler(v_handler)
        v_handler = logging.StreamHandler()
        v_handler.setFormatter(v_formatter)
        self._logger.addHandler(v_handler)

    def log(self, p_message: str) -> None:
        self._logger.info(p_message)


def log(p_logger: Logger, p_messages: []):
    if p_logger and p_messages and len(p_messages) > 0:
        for v_message in p_messages:
            p_logger.log(v_message)
