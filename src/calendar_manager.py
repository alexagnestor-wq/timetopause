import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional


class CalendarManager:
    SCOPES        = ['https://www.googleapis.com/auth/calendar.readonly']
    POLL_INTERVAL = 60  # seconds between calendar checks

    def __init__(
        self,
        data_dir: Path,
        lead_minutes: int = 10,
        on_event: Callable = None,          # (title: str, minutes_until: int)
        on_status_change: Callable = None,  # (connected: bool)
    ):
        self.data_dir         = data_dir
        self.lead_minutes     = lead_minutes
        self.on_event         = on_event
        self.on_status_change = on_status_change

        # credentials.json bundled in assets/ by the developer
        bundled = Path(__file__).parent.parent / 'assets' / 'credentials.json'
        self.credentials_file = bundled if bundled.exists() else data_dir / 'credentials.json'
        self.token_file       = data_dir / 'calendar_token.json'

        self._service = None
        self._stop_event = threading.Event()
        self._polling_thread: Optional[threading.Thread] = None
        self._notified_events: dict = {}  # event_id -> datetime notified

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_authenticated(self) -> bool:
        return self.token_file.exists()

    def has_credentials(self) -> bool:
        return self.credentials_file.exists()

    def authenticate(self):
        """Open OAuth2 browser flow in a background thread."""
        threading.Thread(target=self._auth_thread, daemon=True).start()

    def start_polling(self):
        if self._polling_thread and self._polling_thread.is_alive():
            return
        self._stop_event.clear()
        self._polling_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._polling_thread.start()

    def stop_polling(self):
        self._stop_event.set()

    def update_lead_minutes(self, minutes: int):
        self.lead_minutes = minutes

    def disconnect(self):
        self.stop_polling()
        self._service = None
        if self.token_file.exists():
            self.token_file.unlink()
        if self.on_status_change:
            self.on_status_change(False)

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _auth_thread(self):
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials

            creds = None
            if self.token_file.exists():
                creds = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        print("[CALENDAR] credentials.json not found in", self.data_dir)
                        if self.on_status_change:
                            self.on_status_change(False)
                        return
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), self.SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(self.token_file, 'w') as f:
                    f.write(creds.to_json())

            self._build_service(creds)
            if self.on_status_change:
                self.on_status_change(True)
            self.start_polling()

        except Exception as e:
            print(f"[CALENDAR] Auth error: {e}")
            if self.on_status_change:
                self.on_status_change(False)

    def _build_service(self, creds):
        from googleapiclient.discovery import build
        self._service = build('calendar', 'v3', credentials=creds)

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def _poll_loop(self):
        # Load service from saved token if not already loaded
        if not self._service and self.token_file.exists():
            try:
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import Request
                creds = Credentials.from_authorized_user_file(
                    str(self.token_file), self.SCOPES)
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    with open(self.token_file, 'w') as f:
                        f.write(creds.to_json())
                self._build_service(creds)
            except Exception as e:
                print(f"[CALENDAR] Poll init error: {e}")
                return

        while not self._stop_event.is_set():
            self._check_events()
            self._stop_event.wait(self.POLL_INTERVAL)

    def _check_events(self):
        if not self._service:
            return
        try:
            now = datetime.now(timezone.utc)

            # Expire old notified events (older than 2 hours)
            cutoff = now - timedelta(hours=2)
            self._notified_events = {
                k: v for k, v in self._notified_events.items() if v > cutoff
            }

            # Look in window: [lead - 1 min, lead + 1 min]
            # Tight window so alert fires close to the configured lead time
            time_min = (now + timedelta(minutes=self.lead_minutes - 1)).isoformat()
            time_max = (now + timedelta(minutes=self.lead_minutes + 1)).isoformat()

            result = self._service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            for event in result.get('items', []):
                event_id = event['id']
                if event_id in self._notified_events:
                    continue

                title = event.get('summary', 'Untitled Event')
                start_str = event['start'].get('dateTime', event['start'].get('date'))

                minutes_until = self.lead_minutes
                if 'T' in start_str:
                    start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    minutes_until = max(1, int((start_dt - now).total_seconds() / 60))

                self._notified_events[event_id] = now
                print(f"[CALENDAR] Upcoming: '{title}' in {minutes_until} min")

                if self.on_event:
                    self.on_event(title, minutes_until)

        except Exception as e:
            print(f"[CALENDAR] Check error: {e}")
