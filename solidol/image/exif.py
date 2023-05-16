from piexif import load, TAGS, InvalidImageDataError
from datetime import datetime, timedelta
from pathlib import Path


class EXIF:

    IFD0 = "IFD0"
    IFD1 = "IFD1"
    EXIFIFD = "EXIFIFD"
    GPSIFD = "GPSIFD"

    class Exception(Exception):

        pass

    @staticmethod
    def _exif_geo_values_to_value(p_values: []):
        v_result = 0
        if len(p_values) > 0:
            try:
                v_result = float(p_values[0])
            except (ValueError, OverflowError):
                EXIF.Exception(f"Invalid input value: {p_values[0]}")
            if len(p_values) > 1:
                try:
                    v_result = v_result + float(p_values[1]) / 60
                except (ValueError, OverflowError):
                    EXIF.Exception(f"Invalid input value: {p_values[1]}")
            if len(p_values) > 2:
                try:
                    v_result = v_result + float(p_values[2]) / 3600
                except (ValueError, OverflowError):
                    EXIF.Exception(f"Invalid input value: {p_values[2]}")
            return v_result
        else:
            raise EXIF.Exception("Empty input value")

    @staticmethod
    def _exif_values_to_latitude(p_values: [] = None, p_reference: str = None):
        v_result = EXIF._exif_geo_values_to_value(p_values)
        if v_result and p_reference == "S":
            v_result = -v_result
        return v_result

    @staticmethod
    def _exif_values_to_longitude(p_values: [] = None, p_reference: str = None):
        v_result = EXIF._exif_geo_values_to_value(p_values)
        if v_result and p_reference == "W":
            v_result = -v_result
        return v_result

    @staticmethod
    def _exif_value_to_altitude(p_value: str = None):
        try:
            v_result = float(p_value)
        except (ValueError, OverflowError):
            raise EXIF.Exception(f"Invalid input value: {p_value}")
        return v_result

    @staticmethod
    def gps_values_to_date_time(p_date_value: str, p_time_values: []):
        try:
            v_date = datetime.strptime(p_date_value, "%Y:%m:%d")
        except ValueError:
            raise EXIF.Exception(f"Invalid date input value: {p_date_value}")
        try:
            v_time = timedelta(
                hours=int(float(p_time_values[0])),
                minutes=int(float(p_time_values[1])),
                seconds=int(float(p_time_values[2]))
            )
        except (ValueError, OverflowError):
            raise EXIF.Exception(f"Invalid time input value: {p_time_values}")
        return v_date + v_time

    @staticmethod
    def convert_value_to_datetime(p_value: str) -> datetime:
        try:
            return datetime.strptime(p_value, "%Y:%m:%d %H:%M:%S")
        except ValueError:
            raise EXIF.Exception(f"Invalid input value: {p_value}")

    @staticmethod
    def extract(p_path: str):

        _ifd_names = {
            "0th": EXIF.IFD0,
            "1st": EXIF.IFD1,
            "Exif": EXIF.EXIFIFD,
            "GPS": EXIF.GPSIFD
        }

        if Path(p_path).is_file():
            try:
                v_dict = load(p_path)
            except InvalidImageDataError:
                raise EXIF.Exception("Invalid image file format")
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
            raise EXIF.Exception(f"File '{Path(p_path).name}' not found")
