import os
from abc import ABC, abstractmethod
from typing import Tuple

from scan_batcher.recorder import log, Recorder
from scan_batcher.calculator import Calculator


class Batch(ABC):
    """
    Abstract base class for all data sources used in batch processing.
    """

    def __next__(self) -> dict | None:
        """
        Infinitely yield batch parameters.

        Returns:
            dict: Batch parameters.
        """
        return None

    @abstractmethod
    def __iter__(self):
        """
        Return self as the iterator object.

        Returns:
            Batch: The iterator object itself.
        """
        return self


class Calculate(Batch):
    """
    Batch for a single calculation of optimal scan parameters.
    """

    def __init__(
        self,
        recorder: Recorder | None = None,
        min_dpi: int | None = None,
        max_dpi: int | None = None,
        dpis: list[int] | None = None,
        rounding: str = "nr"
    ):
        """
        Initialize the Calculate batch.

        Args:
            recorder (Recorder, optional): Recorder instance for logging.
            min_dpi (int, optional): Minimum allowed DPI.
            max_dpi (int, optional): Maximum allowed DPI.
            dpis (List[int], optional): List of available DPI values.
            rounding (str, optional): Rounding strategy ('nr', 'mx', 'mn').
        """
        self.recorder = recorder
        self.calculator = Calculator()
        self.min_dpi = min_dpi
        self.max_dpi = max_dpi
        self.dpis = dpis if dpis is not None else []
        self.rounding = rounding

    def _get_user_input(self):
        """
        Prompt the user for required scan parameters and log the input.

        Returns:
            Tuple[float, int]: The photo minimum side (cm) and image minimum side (px).
        """
        log(self.recorder, ["Requesting user input for scan parameters"])
        print("\nEnter scan parameters")
        photo_min_side = self._get_float_input("Minimum photo side length in centimeters: ")
        image_min_side = self._get_int_input("Minimum image side length in pixels: ")

        log(self.recorder, [f"User input: photo_min_side={photo_min_side}, image_min_side={image_min_side}"])
        return photo_min_side, image_min_side

    def _get_float_input(self, prompt: str) -> float:
        """
        Get a float input from the user with error handling.

        Args:
            prompt (str): Prompt to display.

        Returns:
            float: The user input as a float.
        """
        while True:
            try:
                value = float(input(prompt))
                log(self.recorder, [f"Float input received: {value}"])
                return value
            except ValueError:
                print("Error: Enter a number")
                log(self.recorder, ["Invalid float input"])

    def _get_int_input(self, prompt: str, default: int | None = None) -> int:
        """
        Get an integer input from the user with error handling.

        Args:
            prompt (str): Prompt to display.
            default (int, optional): Default value if input is empty.

        Returns:
            int: The user input as an integer.
        """
        while True:
            try:
                value = input(prompt)
                if default is not None and value == "":
                    log(self.recorder, [f"Default integer input used: {default}"])
                    return default
                int_value = int(value)
                log(self.recorder, [f"Integer input received: {int_value}"])
                return int_value
            except ValueError:
                print("Error: Enter an integer")
                log(self.recorder, ["Invalid integer input"])

    def _print_row(self, num: str, dpi: str, px: str, note: str = "") -> None:
        """
        Print a formatted table row with aligned columns.

        Args:
            num (str): Column 1 content (width 3, right-aligned).
            dpi (str): Column 2 content (width 10, left-aligned).
            px (str): Column 3 content (width 10, left-aligned).
            note (str, optional): Column 4 content (width 20, left-aligned).
        """
        print(f"{num:>3}\t{dpi:>10}\t{px:>10}\t{note:<20}")

    def _print_table(self, dpis: list[Tuple[int, int]], rec_dpi: float | None = None, calc_dpi: float | None = None) -> None:
        """
        Print a table of DPI calculation results.

        Args:
            dpis (List[Tuple[int, int]]): List of (DPI, pixels) tuples.
            rec_dpi (float, optional): Recommended DPI value.
            calc_dpi (float, optional): Calculated DPI value.
        """
        log(self.recorder, ["Printing calculation results table"])
        print("\nCalculation results:")
        self._print_row("", "DPI", "pixels", "Note")
        for index, item in enumerate(dpis, start=1):
            self._print_row(
                f"{index}",
                f"{item[0]:.1f}",
                f"{item[1]}",
                note=(
                    "recommended" if item[0] == rec_dpi else
                    "calculated" if item[0] == calc_dpi else ""
                )
            )

    def _next(self) -> dict:
        """
        Perform a single calculation or data retrieval.

        Returns:
            dict: Dictionary with calculation or file data.
        """
        log(self.recorder, ["Starting calculation step"])
        photo_min_side, image_min_side = self._get_user_input()

        # Calculate DPI using internal calculator
        calc_dpi, rec_dpi, dpis = self.calculator(
            float(photo_min_side),
            int(image_min_side),
            int(self.min_dpi) if self.min_dpi is not None else None,
            int(self.max_dpi) if self.max_dpi is not None else None,
            self.dpis,
            self.rounding
        )
        log(self.recorder, [f"Calculator returned: calc_dpi={calc_dpi}, rec_dpi={rec_dpi}, dpis={dpis}"])

        # Convert dpis to set for uniqueness
        dpis = set(dpis)

        # Add calculated values if not present
        if calc_dpi is not None:
            dpis.add((int(calc_dpi), int(photo_min_side * calc_dpi / 2.54)))
        if rec_dpi is not None:
            dpis.add((int(rec_dpi), int(photo_min_side * rec_dpi / 2.54)))

        # Sort for display, but work with set
        dpis = sorted(dpis, key=lambda x: x[0])

        self._print_table(dpis, rec_dpi, calc_dpi)

        while True:
            try:
                # Get user input for DPI selection
                if rec_dpi is not None:
                    index = self._get_int_input(
                        "\nSelect a DPI by entering the corresponding # from the table above (press Enter to use the recommended one): ",
                        0
                    )
                else:
                    index = self._get_int_input(
                        "\nSelect a DPI by entering the corresponding # from the table above: "
                    )
                if index == 0:  # Default case
                    dpi = rec_dpi
                    log(self.recorder, [f"User selected recommended DPI: {dpi}"])
                    print("\nUsing recommended DPI:", dpi)
                    break
                elif 1 <= index <= len(dpis):
                    dpi = dpis[index - 1][0]  # Get DPI from the selected index
                    log(self.recorder, [f"User selected DPI: {dpi}"])
                    print("\nSelected DPI:", dpi)
                    break
                else:
                    print("Error: Invalid selection. Please try again.")
                    log(self.recorder, ["Invalid DPI selection"])
            except ValueError:
                print("Error: Invalid number entered.")
                log(self.recorder, ["Invalid number entered for DPI selection"])
        log(self.recorder, [f"Calculation finished, returning scan_dpi={dpi}"])
        return {"scan_dpi": dpi}

    def __iter__(self):
        """
        Return self as the iterator object.

        Returns:
            Calculate: The iterator object itself.
        """
        return self

    def __next__(self) -> dict | None:
        """
        Perform a single calculation and raise StopIteration.

        Raises:
            StopIteration: Always raised after one calculation.
        """
        self._next()
        raise StopIteration


class Scan(Calculate):
    """
    Data source from scanner (infinite) with built-in DPI calculation.
    """

    def __next__(self) -> dict | None:
        """
        Infinitely yield scan parameters with calculated DPI.

        Returns:
            dict: Scan parameters with calculated DPI.
        """
        return self._next()


class Process(Batch):
    """
    Data source from a folder (original version).

    Iterates over files in a directory matching a filter and yields file info.
    """

    def __init__(self, path, file_filter="*.*"):
        """
        Initialize the Process batch.

        Args:
            path (str): Path to the folder.
            file_filter (str, optional): File filter pattern (default: "*.*").
        """
        self.path = path
        self.file_filter = file_filter
        self._validate_path()
        self._files = self._get_matching_files()
        self._index = 0  # Current index for iteration

    def _validate_path(self):
        """
        Validate that the specified path exists and is a directory.

        Raises:
            ValueError: If the folder does not exist.
        """
        if not os.path.isdir(self.path):
            raise ValueError(f"Folder doesn't exist: {self.path}")

    def _get_matching_files(self):
        """
        Get a list of files in the directory matching the filter.

        Returns:
            List[str]: List of matching file names.
        """
        return [
            f for f in os.listdir(self.path)
            if self._matches_filter(f) and os.path.isfile(os.path.join(self.path, f))
        ]

    def _matches_filter(self, filename):
        """
        Check if a filename matches the file filter.

        Args:
            filename (str): The filename to check.

        Returns:
            bool: True if the file matches the filter, False otherwise.
        """
        if self.file_filter == "*.*":
            return True
        ext = os.path.splitext(filename)[1].lower()
        filter_ext = self.file_filter.lower()
        if filter_ext.startswith("*"):
            return ext == filter_ext[1:] or ext == filter_ext[2:]
        return ext == filter_ext if filter_ext.startswith(".") else filename.lower().endswith(filter_ext.lower())

    def __iter__(self):
        """
        Return self as the iterator object and reset the index.

        Returns:
            Process: The iterator object itself.
        """
        self._index = 0  # Reset index for each new iterator
        return self

    def __next__(self):
        """
        Return the next file info or raise StopIteration when done.

        Returns:
            dict: Dictionary with file path and filename.

        Raises:
            StopIteration: When all files have been processed.
        """
        if self._index < len(self._files):
            filename = self._files[self._index]
            self._index += 1
            return {
                "path": os.path.join(self.path, filename),
                "filename": filename
            }
        raise StopIteration
