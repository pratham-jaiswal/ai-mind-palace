from datetime import datetime
from zoneinfo import ZoneInfo

class GenericTools:
    def __init__(self, tz_name: str):
        self.tz_name = tz_name

    def convert_to_utc(self, datetime_str: str) -> str:
        """
        Convert a datetime string in the user's pre-defined timezone to UTC ISO 8601 format.
        Args:
            datetime_str (str): The datetime string in ISO 8601 format (e.g., "2023-10-01T12:00:00").

        Returns:
            str: The UTC datetime string in ISO 8601 format.
        """
        local_tz = ZoneInfo(self.tz_name)
        local_dt = datetime.fromisoformat(datetime_str)
        local_dt = local_dt.replace(tzinfo=local_tz)
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        return utc_dt.isoformat()

    def convert_from_utc(self, datetime_str: str) -> str:
        """
        Convert a datetime string in UTC to the user's pre-defined timezone.
        Args:
            datetime_str (str): The UTC datetime string in ISO 8601 format (e.g., "2023-10-01T06:30:00+00:00").

        Returns:
            str: The datetime string in the user's timezone in ISO 8601 format.
        """
        utc_dt = datetime.fromisoformat(datetime_str)
        if utc_dt.tzinfo is None:
            utc_dt = utc_dt.replace(tzinfo=ZoneInfo("UTC"))
        local_dt = utc_dt.astimezone(ZoneInfo(self.tz_name))
        return local_dt.isoformat()

    def get_current_datetime(self) -> str:
        """
        Get the current datetime in the user's pre-defined timezone.

        Returns:
            str: The current datetime in ISO 8601 format for the specified timezone.
        """
        local_tz = ZoneInfo(self.tz_name)
        return datetime.now(local_tz).isoformat()
