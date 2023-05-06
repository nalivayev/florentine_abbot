from argparse import ArgumentParser
from typing import Any


class CalculatorParser(ArgumentParser):

    _required_group: Any

    def __init__(self):
        ArgumentParser.__init__(self)
        self._required_group = self.add_argument_group("required arguments")
        self._required_group.add_argument(
            "-pl",
            "--photolength",
            type=float,
            help="the length of the larger side of the photo in centimeters"
        )
        self._required_group.add_argument(
            "-il",
            "--imagelength",
            type=int,
            help="the desired length of the larger side of the digitized image in pixels"
        )
        self.add_argument(
            "-minr",
            "--minimalresolution",
            type=int,
            help="minimum resolution when scanning in dpi"
        )
        self.add_argument(
            "-maxr",
            "--maximalresolution",
            type=int,
            help="maximal resolution when scanning in dpi"
        )
        self.add_argument(
            "-rl",
            "--resolutionlist",
            type=int,
            nargs="+"
        )

    def parse_args(self, args=None, namespace=None):
        v_result = ArgumentParser.parse_args(self, args, namespace)
        if v_result.photolength:
            if v_result.photolength <= 0:
                self.error("Incorrect length of the larger side of the photo")
        else:
            self.error("Incorrect length of the larger side of the photo")
        if v_result.imagelength:
            if v_result.imagelength <= 0:
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
        v_args.photolength,
        v_args.imagelength,
        v_args.minimalresolution,
        v_args.maximalresolution,
        v_args.resolutionlist
    )


if __name__ == "__main__":
    main()
