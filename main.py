import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()  # leest .env in

CLIENT_ID      = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET  = os.getenv("STRAVA_CLIENT_SECRET")
REFRESH_TOKEN  = os.getenv("STRAVA_REFRESH_TOKEN")

TOKEN_URL      = "https://www.strava.com/api/v3/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

def refresh_access_token() -> dict:
    """Vernieuwt de access‑token met de refresh‑token."""
    resp = requests.post(
        TOKEN_URL,
        data={
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type":    "refresh_token",
            "refresh_token": REFRESH_TOKEN,
        },
        timeout=15,
    )
    resp.raise_for_status()
    token_data = resp.json()
    # token_data bevat: access_token, expires_at, refresh_token (nieuw!), ...
    return token_data

def get_activities(after_epoch: int = None, per_page: int = 30):
    """Haalt activiteiten op sinds 'after_epoch' (Unix‑tijdstamp, optioneel)."""
    token_data = refresh_access_token()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    params = {"per_page": per_page, "page": 1}
    if after_epoch:
        params["after"] = after_epoch

    resp = requests.get(ACTIVITIES_URL, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # voorbeeld: activiteiten van de laatste 7 dagen
    seven_days_ago = int(time.time()) - 7 * 24 * 3600
    activities = get_activities(after_epoch=seven_days_ago)
    for a in activities:
        print(f"{a['name']} – {a['distance']/1000:.1f} km op {a['start_date_local']}")
