from piexif import load, TAGS, InvalidImageDataError
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class Exifer:
    """
    Utility class for extracting and converting EXIF metadata from images.

    Provides static methods for parsing GPS coordinates, altitude, date/time, and extracting EXIF tags.
    """

    IFD0 = "IFD0"
    IFD1 = "IFD1"
    EXIFIFD = "EXIFIFD"
    GPSIFD = "GPSIFD"

    class Exception(Exception):
        """Exception raised for EXIF-related errors."""
        pass

    @staticmethod
    def _exif_geo_values_to_value(p_values: List) -> float:
        """
        Convert a list of EXIF GPS coordinate values (degrees, minutes, seconds) to a float.

        Args:
            p_values (List): List of coordinate components (usually 3 elements).

        Returns:
            float: The coordinate as a float.

        Raises:
            Exifer.Exception: If input is empty or contains invalid values.
        """
        v_result = 0
        if len(p_values) > 0:
            try:
                v_result = float(p_values[0])
            except (ValueError, OverflowError):
                raise Exifer.Exception(f"Invalid input value: {p_values[0]}")
            if len(p_values) > 1:
                try:
                    v_result = v_result + float(p_values[1]) / 60
                except (ValueError, OverflowError):
                    raise Exifer.Exception(f"Invalid input value: {p_values[1]}")
            if len(p_values) > 2:
                try:
                    v_result = v_result + float(p_values[2]) / 3600
                except (ValueError, OverflowError):
                    raise Exifer.Exception(f"Invalid input value: {p_values[2]}")
            return v_result
        else:
            raise Exifer.Exception("Empty input value")

    @staticmethod
    def _exif_values_to_latitude(p_values: List = None, p_reference: str = None) -> float:
        """
        Convert EXIF GPS latitude values and reference to a signed float.

        Args:
            p_values (List): List of latitude components.
            p_reference (str): 'N' for north, 'S' for south.

        Returns:
            float: Latitude as a signed float.
        """
        v_result = Exifer._exif_geo_values_to_value(p_values)
        if v_result and p_reference == "S":
            v_result = -v_result
        return v_result

    @staticmethod
    def _exif_values_to_longitude(p_values: List = None, p_reference: str = None) -> float:
        """
        Convert EXIF GPS longitude values and reference to a signed float.

        Args:
            p_values (List): List of longitude components.
            p_reference (str): 'E' for east, 'W' for west.

        Returns:
            float: Longitude as a signed float.
        """
        v_result = Exifer._exif_geo_values_to_value(p_values)
        if v_result and p_reference == "W":
            v_result = -v_result
        return v_result

    @staticmethod
    def _exif_value_to_altitude(p_value: str = None) -> float:
        """
        Convert EXIF altitude value to float.

        Args:
            p_value (str): Altitude value as string.

        Returns:
            float: Altitude.

        Raises:
            Exifer.Exception: If the value cannot be converted.
        """
        try:
            v_result = float(p_value)
        except (ValueError, OverflowError):
            raise Exifer.Exception(f"Invalid input value: {p_value}")
        return v_result

    @staticmethod
    def gps_values_to_date_time(p_date_value: str, p_time_values: List) -> datetime:
        """
        Convert EXIF GPS date and time values to a datetime object.

        Args:
            p_date_value (str): Date string in format 'YYYY:MM:DD'.
            p_time_values (List): List of [hour, minute, second] values.

        Returns:
            datetime: Combined date and time.

        Raises:
            Exifer.Exception: If date or time values are invalid.
        """
        try:
            v_date = datetime.strptime(p_date_value, "%Y:%m:%d")
        except ValueError:
            raise Exifer.Exception(f"Invalid date input value: {p_date_value}")
        try:
            v_time = timedelta(
                hours=int(float(p_time_values[0])),
                minutes=int(float(p_time_values[1])),
                seconds=int(float(p_time_values[2]))
            )
        except (ValueError, OverflowError):
            raise Exifer.Exception(f"Invalid time input value: {p_time_values}")
        return v_date + v_time

    @staticmethod
    def convert_value_to_datetime(p_value: str) -> datetime:
        """
        Convert EXIF date/time string to a datetime object.

        Args:
            p_value (str): Date/time string in format 'YYYY:MM:DD HH:MM:SS'.

        Returns:
            datetime: Parsed datetime object.

        Raises:
            Exifer.Exception: If the value cannot be parsed.
        """
        try:
            return datetime.strptime(p_value, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            raise Exifer.Exception(f"Invalid input value: {p_value}")

    @staticmethod
    def extract(p_path: str) -> dict:
        """
        Extract EXIF tags from an image file.

        Args:
            p_path (str): Path to the image file.

        Returns:
            dict: Dictionary of EXIF tags grouped by IFD section.

        Raises:
            Exifer.Exception: If the file does not exist or is not a valid image.
        """
        _ifd_names = {
            "0th": Exifer.IFD0,
            "1st": Exifer.IFD1,
            "Exif": Exifer.EXIFIFD,
            "GPS": Exifer.GPSIFD
        }

        if Path(p_path).is_file():
            try:
                v_dict = load(p_path)
            except InvalidImageDataError:
                raise Exifer.Exception("Invalid image file format")
            v_tags = {}
            for v_ifd in ("0th", "Exif", "GPS", "1st"):
                for v_tag in v_dict[v_ifd]:
                    v_name = TAGS.get(v_ifd, {}).get(v_tag, {}).get("name", None)
                    v_value = v_dict.get(v_ifd, {}).get(v_tag, None)
                    if v_name and v_value:
                        if _ifd_names[v_ifd] not in v_tags:
                            v_tags[_ifd_names[v_ifd]] = {}
                        v_tags[_ifd_names[v_ifd]][v_name] = v_value
            return v_tags
        else:
            raise Exifer.Exception(f"File '{Path(p_path).name}' not found")
