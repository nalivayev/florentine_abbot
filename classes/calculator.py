class Calculator:
    """
    A calculator class for determining optimal DPI (dots per inch) values for image printing.
    
    The calculator takes into account photo dimensions, image dimensions, DPI constraints,
    and provides recommended DPI values based on different rounding strategies.
    """
    
    def __call__(self, photo_width, photo_height, image_width, image_height, minimal_dpi, maximal_dpi, dpi_list, rounding) -> tuple:
        """
        Calculate the optimal DPI values for printing an image on a photo with given dimensions.
        
        Args:
            photo_width: Width of the photo in centimeters
            photo_height: Height of the photo in centimeters
            image_width: Width of the image in pixels
            image_height: Height of the image in pixels
            minimal_dpi: Minimum allowed DPI value (can be None)
            maximal_dpi: Maximum allowed DPI value (can be None)
            dpi_list: List of available DPI values to choose from
            rounding: Rounding strategy ('nr' for nearest, 'mx' for max, 'mn' for min)
            
        Returns:
            tuple: Contains three elements:
                - calculated_dpi: The raw calculated DPI value
                - recommended_dpi: The recommended DPI after applying constraints and rounding
                - dpi_options: List of tuples with available DPI options and corresponding pixel dimensions
        """
        photo_long_size = max(photo_width, photo_height)
        photo_short_size = min(photo_width, photo_height)
        image_long_size = max(image_width, image_height)
        image_short_size = min(image_width, image_height)
        dpi_list = sorted(dpi_list) if dpi_list else []
        if minimal_dpi:
            if len(dpi_list) > 0:
                minimal_dpi = dpi_list[0] if dpi_list[0] > minimal_dpi else minimal_dpi
            else:
                minimal_dpi = minimal_dpi
        else:
            minimal_dpi = dpi_list[0] if len(dpi_list) > 0 else None
        if maximal_dpi:
            if len(dpi_list) > 0:
                maximal_dpi = dpi_list[-1] if dpi_list[-1] < maximal_dpi else maximal_dpi
            else:
                maximal_dpi = maximal_dpi
        else:
            maximal_dpi = dpi_list[-1] if len(dpi_list) > 0 else None
        calculated_width_dpi = image_long_size / (photo_long_size / 2.54)
        calculated_height_dpi = image_short_size / (photo_short_size / 2.54)
        calculated_dpi = max(calculated_width_dpi, calculated_height_dpi)
        recommended_dpi = calculated_dpi
        for index, value in enumerate(dpi_list):
            if recommended_dpi < value:
                match rounding:
                    case "nr":
                        if index > 0 and value - recommended_dpi > recommended_dpi - dpi_list[index - 1]:
                            recommended_dpi = dpi_list[index - 1]
                        else:
                            recommended_dpi = value
                    case "mx":
                        recommended_dpi = value
                    case "mn":
                        recommended_dpi = dpi_list[index - 1]
                break
        if minimal_dpi:
            recommended_dpi = max(minimal_dpi, recommended_dpi)
        if maximal_dpi:
            recommended_dpi = min(maximal_dpi, recommended_dpi)
        return (
            calculated_dpi,
            recommended_dpi,
            [(dpi, int(dpi * photo_width / 2.54), int(dpi * photo_height / 2.54)) for dpi in dpi_list]
        )
