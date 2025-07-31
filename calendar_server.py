import os
import datetime
from mcp.server.fastmcp import FastMCP
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv
from dateutil import parser, tz

load_dotenv()
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_API_CREDENTIALS_PATH")
CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Initialize Google Calendar API client
service = None
if GOOGLE_CREDENTIALS:
    try:
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=creds)
    except Exception as e:
        print(f"Error setting up Calendar API: {e}")

mcp = FastMCP("Calendar")

@mcp.tool()
def list_events_for_day(date: str) -> str:
    """
    List all events for a given date (YYYY-MM-DD).
    """
    try:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except Exception as e:
        return f"Invalid date format. Use YYYY-MM-DD. Error: {e}"

    # Define the day range (00:00 to 23:59:59)
    start_of_day = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, 0)
    end_of_day = start_of_day + datetime.timedelta(days=1, seconds=-1)
    time_min = start_of_day.isoformat() + 'Z'
    time_max = end_of_day.isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get('items', [])
        print(events)

        if not events:
            return f"No events found on {date}."
        lines = [f"Events on {date}:"]
        for ev in events:
            start = ev['start'].get('dateTime', ev['start'].get('date'))
            summary = ev.get('summary', 'No Title')
            lines.append(f"- {start}: {summary}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error retrieving events: {e}"

@mcp.tool()
def is_free_at(datetime_str: str) -> bool:
    print(f"[DEBUG] is_free_at called with date_time: {datetime_str}")
    try:
        print(f"Input: {datetime_str}")
        dt = parser.parse(datetime_str)
        print(f"Parsed: {dt}, tzinfo: {dt.tzinfo}")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz.UTC)
        else:
            dt = dt.astimezone(tz.UTC)
    except Exception as e:
        print(f"Parse error: {e}")
        return False

    print(dt)
    day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + datetime.timedelta(days=1)
    time_min = day_start.isoformat()
    time_max = day_end.isoformat()
    print("Inside")
    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        print(events_result)
        for ev in events_result.get('items', []):
            ev_start = parser.parse(ev['start'].get('dateTime', ev['start'].get('date')))
            ev_end = parser.parse(ev['end'].get('dateTime', ev['end'].get('date')))
            ev_start = ev_start.astimezone(tz.UTC)
            ev_end = ev_end.astimezone(tz.UTC)

            print(dt, ev_start, ev_end)
            if ev_start <= dt < ev_end:
                return False
        return True
    except Exception:
        return False

@mcp.tool()
def find_next_free_slot(after_datetime: str, duration_minutes: int) -> str:
    """
    Find the next free time slot after the given datetime that can fit duration.
    Scans until end of the day. Returns a message or ISO time of slot start.
    """
    try:
        after_dt = datetime.datetime.fromisoformat(after_datetime)
    except Exception as e:
        return f"Invalid datetime format. Error: {e}"

    end_of_day = after_dt.replace(hour=23, minute=59, second=59, microsecond=0)
    time_min = after_dt.isoformat() + 'Z'
    time_max = end_of_day.isoformat() + 'Z'

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get('items', [])

        # Add sentinel event at day end
        sentinel_end = {'start': {'dateTime': end_of_day.isoformat()+'Z'},
                        'end': {'dateTime': end_of_day.isoformat()+'Z'}}
        events.append(sentinel_end)

        current_start = after_dt
        for ev in events:
            ev_start = datetime.datetime.fromisoformat(ev['start'].get('dateTime', ev['start'].get('date')))
            gap = (ev_start - current_start).total_seconds() / 60
            if gap >= duration_minutes:
                return f"{current_start.isoformat()} is available for {duration_minutes} minutes."
            # Move past this event
            ev_end = datetime.datetime.fromisoformat(ev['end'].get('dateTime', ev['end'].get('date')))
            if ev_end > current_start:
                current_start = ev_end
        return "No free slot available today for that duration."
    except Exception as e:
        return f"Error finding free slot: {e}"

@mcp.tool()
def schedule_event(summary: str, start_datetime: str, end_datetime: str) -> str:
    """
    Schedule a new event with the given summary and ISO start/end times.
    """
    try:
        event = {'summary': summary,
                 'start': {'dateTime': start_datetime, "timeZone": "Asia/Dhaka"},
                 'end': {'dateTime': end_datetime, "timeZone": "Asia/Dhaka"}}
        created = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        link = created.get('htmlLink', '')
        return f"Event created: {link}"
    except Exception as e:
        return f"Error creating event: {e}"

@mcp.tool()
def update_event(event_id: str, new_summary: str = None, new_start: str = None, new_end: str = None) -> str:
    """
    Update an event's summary or time by its ID.
    """
    try:
        ev = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
        if new_summary:
            ev['summary'] = new_summary
        if new_start:
            ev['start']['dateTime'] = new_start
        if new_end:
            ev['end']['dateTime'] = new_end
        updated = service.events().update(calendarId=CALENDAR_ID, eventId=event_id, body=ev).execute()
        return f"Event updated: {updated.get('htmlLink', '')}"
    except Exception as e:
        return f"Error updating event: {e}"

@mcp.tool()
def cancel_event(event_id: str) -> str:
    """
    Delete (cancel) an event by its ID.
    """
    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return "Event canceled."
    except Exception as e:
        return f"Error canceling event: {e}"

if __name__ == "__main__":
    print('Server Started...')
    mcp.run(transport="stdio")
    # Example test inputs
    # print("Testing list_events_for_day:")
    # print("Input: '2025-07-20'")
    # print("Output:", list_events_for_day('2025-07-20'))
    # print()

    # print("Testing is_free_at:")
    # print("Input: '2025-07-27T23:00:00'")
    # print("Output:", is_free_at('2025-07-27T23:00:00'))
    # print()

    # print("Testing find_next_free_slot:")
    # print("Input: after_datetime='2024-07-20T09:00:00', duration_minutes=30")
    # print("Output:", find_next_free_slot('2024-07-20T09:00:00', 30))
    # print()

    # print("Testing schedule_event:")
    # print("Input: summary='Test Event Tauhid', start_datetime='2025-07-21T15:00:00', end_datetime='2025-07-21T16:00:00'")
    # print("Output:", schedule_event('Test Event', '2025-07-21T19:00:00', '2025-07-21T20:00:00'))
    # print()

    # print("Testing update_event:")
    # print("Input: event_id='<EVENT_ID>', new_summary='Updated Event'")
    # print("Output:", update_event('<EVENT_ID>', new_summary='Updated Event'))
    # print()

    # print("Testing cancel_event:")
    # print("Input: event_id='<EVENT_ID>'")
    # print("Output:", cancel_event('<EVENT_ID>'))
    # print()