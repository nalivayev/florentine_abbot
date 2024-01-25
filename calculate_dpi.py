from classes import CalculatorParser, Calculator


def main():
    v_parser = CalculatorParser()
    v_args = v_parser.parse_args()
    v_calculator = Calculator()
    v_dpi = v_calculator.do(
        v_args.photo_size,
        v_args.image_size,
        v_args.minimal_resolution,
        v_args.maximal_resolution,
        v_args.resolution_list
    )
    print(f"Calculated resolution is {v_dpi[0]} dpi")
    print(f"Recommended resolution is {v_dpi[1]} dpi")


if __name__ == "__main__":
    main()
