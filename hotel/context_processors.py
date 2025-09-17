from datetime import datetime
import calendar
import pytz
from django.utils import timezone

def date_timezone_info(request):
    """Add timezone and date information to context."""
    user_timezone_name = request.COOKIES.get('user_timezone', 'UTC')
    
    try:
        user_timezone = pytz.timezone(user_timezone_name)
    except pytz.exceptions.UnknownTimeZoneError:
        user_timezone = pytz.UTC
        user_timezone_name = 'UTC'
    
    now_utc = timezone.now()
    now_user_tz = now_utc.astimezone(user_timezone)
    
    current_day = now_user_tz.day
    current_month = now_user_tz.month
    current_year = now_user_tz.year
    
    cal = calendar.TextCalendar(calendar.MONDAY)
    text_calendar = cal.formatmonth(current_year, current_month).splitlines()
    
    highlighted_calendar = []
    for line in text_calendar:
        if f"{current_day:2}" in line:
            line = line.replace(f"{current_day:2}", f"[{current_day:2}]")
        highlighted_calendar.append(line)
    
    highlighted_calendar = "\n".join(highlighted_calendar)
    
    return {
        'user_timezone': user_timezone_name,
        'user_current_date': now_user_tz,
        'utc_current_date': now_utc,
        'text_calendar': highlighted_calendar,
    }