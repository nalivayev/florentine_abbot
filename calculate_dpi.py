from classes import CalculatorParser, Calculator


def main():
    v_parser = CalculatorParser()
    v_args = v_parser.parse_args()
    v_calculator = Calculator()
    v_dpi = v_calculator(
        v_args.photo_width,
        v_args.photo_height,
        v_args.image_width,
        v_args.image_height,
        v_args.minimal_resolution,
        v_args.maximal_resolution,
        v_args.resolution_list
    )
    print(f"Calculated resolution is {v_dpi[0]} dpi")
    print(f"Recommended resolution is {v_dpi[1]} dpi")


if __name__ == "__main__":
    main()
