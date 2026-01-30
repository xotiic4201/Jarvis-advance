# tools/time_tool.py
from langchain.tools import tool
from datetime import datetime
import pytz

@tool
def get_time(city: str) -> str:
    """Returns the current time in a given city."""
    try:
        city_timezones = {
            "seattle": "America/Los_Angeles",
            "new york": "America/New_York",
            "london": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "sydney": "Australia/Sydney",
            "los angeles": "America/Los_Angeles",
            "san francisco": "America/Los_Angeles",
            
        }
        city_key = city.lower()
        
        # Adding a shortcut for "pst" or "pacific time"
        if "pst" in city_key or "pacific" in city_key:
            city_key = "los angeles"

        if city_key not in city_timezones:
            return f"Sorry, I don't know the timezone for {city}."

        timezone = pytz.timezone(city_timezones[city_key])
        current_time = datetime.now(timezone).strftime("%I:%M %p")
        return f"The current time in {city.title()} is {current_time}."
    except Exception as e:
        return f"Error: {e}"