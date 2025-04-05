from classes import CalculatorParser, Calculator


def main():
    parser = CalculatorParser()
    args = parser.parse_args()
    calculator = Calculator()
    dpi = calculator(
        args.photo_width,
        args.photo_height,
        args.image_width,
        args.image_height,
        args.minimal_resolution,
        args.maximal_resolution,
        args.resolution_list
    )
    print(f"Calculated resolution is {dpi[0]} dpi")
    print(f"Recommended resolution is {dpi[1]} dpi")


if __name__ == "__main__":
    main()
