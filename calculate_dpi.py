from argparse import ArgumentParser
from typing import Any


class CalculatorParser(ArgumentParser):

    _required_group: Any

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(
            "-pl",
            "--photo_length",
            type=float,
            help="the length of the larger side of the photo in centimeters"
        )
        self._required_group.add_argument(
            "-il",
            "--image_length",
            type=int,
            help="the desired length of the larger side of the digitized image in pixels"
        )
        self.add_argument(
            "-minr",
            "--minimal_resolution",
            type=int,
            help="minimum resolution when scanning in DPI"
        )
        self.add_argument(
            "-maxr",
            "--maximal_resolution",
            type=int,
            help="maximal resolution when scanning in DPI"
        )
        self.add_argument(
            "-rl",
            "--resolution_list",
            type=int,
            nargs="+",
            help="a list of DPI resolutions supported by the scanner, separated by comma, e.g., '100, 300, 1200'"
        )

    def parse_args(self, p_args=None, p_namespace=None):
        v_result = ArgumentParser.parse_args(self, p_args, p_namespace)
        if v_result.photo_length:
            if v_result.photo_length <= 0:
                self.error("Incorrect length of the larger side of the photo")
        else:
            self.error("Incorrect length of the larger side of the photo")
        if v_result.image_length:
            if v_result.image_length <= 0:
                self.error("Incorrect desired length of the larger side of the digitized image in pixels")
        else:
            self.error("Incorrect desired length of the larger side of the digitized image in pixels")
        return v_result


class Calculator:

    @staticmethod
    def do(p_photo_length, p_image_length, p_minimal_resolution, p_maximal_resolution, p_resolution_list):
        v_resolution_list = sorted(p_resolution_list) if p_resolution_list else []
        v_photo_length_in_inches = p_photo_length / 2.54
        v_dpi = p_image_length / v_photo_length_in_inches
        if p_minimal_resolution:
            if len(v_resolution_list) > 0:
                if v_resolution_list[0] > p_minimal_resolution:
                    v_minimal_resolution = v_resolution_list[0]
                else:
                    v_minimal_resolution = p_minimal_resolution
            else:
                v_minimal_resolution = p_minimal_resolution
        else:
            if len(v_resolution_list) > 0:
                v_minimal_resolution = v_resolution_list[0]
            else:
                v_minimal_resolution = None
        if p_maximal_resolution:
            if len(v_resolution_list) > 0:
                if v_resolution_list[len(v_resolution_list) - 1] < p_maximal_resolution:
                    v_maximal_resolution = v_resolution_list[len(v_resolution_list) - 1]
                else:
                    v_maximal_resolution = p_maximal_resolution
            else:
                v_maximal_resolution = p_maximal_resolution
        else:
            if len(v_resolution_list) > 0:
                v_maximal_resolution = v_resolution_list[len(v_resolution_list) - 1]
            else:
                v_maximal_resolution = None
        print(f"Calculated resolution is {v_dpi} dpi")
        for v_i in v_resolution_list:
            if v_dpi < v_i:
                v_dpi = v_i
                break
        if v_minimal_resolution:
            v_dpi = max(v_minimal_resolution, v_dpi)
        if v_maximal_resolution:
            v_dpi = min(v_maximal_resolution, v_dpi)
        print(f"Recommended resolution is {v_dpi} dpi")


def main():
    v_parser = CalculatorParser()
    v_args = v_parser.parse_args()
    v_calculator = Calculator()
    v_calculator.do(
        v_args.photo_length,
        v_args.image_length,
        v_args.minimal_resolution,
        v_args.maximal_resolution,
        v_args.resolution_list
    )


if __name__ == "__main__":
    main()
