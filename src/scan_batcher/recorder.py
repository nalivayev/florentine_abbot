from logging import Logger, getLogger, FileHandler, Formatter, INFO


class Recorder:
    """Logger wrapper for convenient logging to a file."""

    _logger: Logger

    def __init__(self, path: str, category: str):
        """
        Initialize the recorder with file output.

        Args:
            path (str): Path to the log file.
            category (str): Logger category name.
        """
        self._logger = getLogger(category)
        self._logger.setLevel(INFO)
        formatter = Formatter("%(asctime)s.%(msecs)03d %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
        handler = FileHandler(f"{path}", mode="w")
        handler.setFormatter(formatter)
        if not self._logger.handlers:
            self._logger.addHandler(handler)

    def log(self, message: str) -> None:
        """
        Log a single message.

        Args:
            message (str): Message to log.
        """
        self._logger.info(message)


def log(recorder: Recorder | None, messages: list[str]) -> None:
    """
    Log multiple messages using the provided recorder.

    Args:
        recorder (Recorder): Recorder instance to use (can be None).
        messages (List[str]): List of messages to log.
    """
    if recorder:
        for message in messages:
            recorder.log(message)
