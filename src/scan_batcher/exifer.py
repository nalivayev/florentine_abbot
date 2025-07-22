from piexif import load, TAGS, InvalidImageDataError
from datetime import datetime, timedelta
from pathlib import Path


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
    def _exif_geo_values_to_value(values: list| None) -> float:
        """
        Convert a list of EXIF GPS coordinate values (degrees, minutes, seconds) to a float.

        Args:
            values (List): List of coordinate components (usually 3 elements).

        Returns:
            float: The coordinate as a float.

        Raises:
            Exifer.Exception: If input is empty or contains invalid values.
        """
        result = 0
        if values and len(values) > 0:
            try:
                result = float(values[0])
            except (ValueError, OverflowError):
                raise Exifer.Exception(f"Invalid input value: {values[0]}")
            if len(values) > 1:
                try:
                    result = result + float(values[1]) / 60
                except (ValueError, OverflowError):
                    raise Exifer.Exception(f"Invalid input value: {values[1]}")
            if len(values) > 2:
                try:
                    result = result + float(values[2]) / 3600
                except (ValueError, OverflowError):
                    raise Exifer.Exception(f"Invalid input value: {values[2]}")
            return result
        else:
            raise Exifer.Exception("Empty input value")

    @staticmethod
    def _exif_values_to_latitude(values: list | None = None, reference: str | None = None) -> float:
        """
        Convert EXIF GPS latitude values and reference to a signed float.

        Args:
            values (List): List of latitude components.
            reference (str): 'N' for north, 'S' for south.

        Returns:
            float: Latitude as a signed float.
        """
        result = Exifer._exif_geo_values_to_value(values)
        if result and reference == "S":
            result = -result
        return result

    @staticmethod
    def _exif_values_to_longitude(values: list | None = None, reference: str | None = None) -> float:
        """
        Convert EXIF GPS longitude values and reference to a signed float.

        Args:
            values (List): List of longitude components.
            reference (str): 'E' for east, 'W' for west.

        Returns:
            float: Longitude as a signed float.
        """
        result = Exifer._exif_geo_values_to_value(values)
        if result and reference == "W":
            result = -result
        return result

    @staticmethod
    def _exif_value_to_altitude(value: str | None = None) -> float:
        """
        Convert EXIF altitude value to float.

        Args:
            value (str): Altitude value as string.

        Returns:
            float: Altitude.

        Raises:
            Exifer.Exception: If the value cannot be converted or is None.
        """
        if not value:
            raise Exifer.Exception(f"Invalid input value: {value}")
        
        try:
            return float(value)
        except (ValueError, OverflowError):
            raise Exifer.Exception(f"Invalid input value: {value}")
        
    @staticmethod
    def gps_values_to_date_time(date_value: str, time_values: list) -> datetime:
        """
        Convert EXIF GPS date and time values to a datetime object.

        Args:
            date_value (str): Date string in format 'YYYY:MM:DD'.
            time_values (List): List of [hour, minute, second] values.

        Returns:
            datetime: Combined date and time.

        Raises:
            Exifer.Exception: If date or time values are invalid.
        """
        try:
            date = datetime.strptime(date_value, "%Y:%m:%d")
        except ValueError:
            raise Exifer.Exception(f"Invalid date input value: {date_value}")
        try:
            time = timedelta(
                hours=int(float(time_values[0])),
                minutes=int(float(time_values[1])),
                seconds=int(float(time_values[2]))
            )
        except (ValueError, OverflowError):
            raise Exifer.Exception(f"Invalid time input value: {time_values}")
        return date + time

    @staticmethod
    def convert_value_to_datetime(value: str) -> datetime:
        """
        Convert EXIF date/time string to a datetime object.

        Args:
            value (str): Date/time string in format 'YYYY:MM:DD HH:MM:SS'.

        Returns:
            datetime: Parsed datetime object.

        Raises:
            Exifer.Exception: If the value cannot be parsed.
        """
        try:
            return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            raise Exifer.Exception(f"Invalid input value: {value}")

    @staticmethod
    def extract(path: str) -> dict:
        """
        Extract EXIF tags from an image file.

        Args:
            path (str): Path to the image file.

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

        if Path(path).is_file():
            try:
                dict = load(path)
            except InvalidImageDataError:
                raise Exifer.Exception("Invalid image file format")
            tags = {}
            for ifd in ("0th", "Exif", "GPS", "1st"):
                for tag in dict[ifd]:
                    name = TAGS.get(ifd, {}).get(tag, {}).get("name", None)
                    value = dict.get(ifd, {}).get(tag, None)
                    if name and value:
                        if _ifd_names[ifd] not in tags:
                            tags[_ifd_names[ifd]] = {}
                        tags[_ifd_names[ifd]][name] = value
            return tags
        else:
            raise Exifer.Exception(f"File '{Path(path).name}' not found")
