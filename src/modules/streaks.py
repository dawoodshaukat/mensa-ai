import json
from datetime import datetime, timedelta

def get_streak():
    filepath = "memory/status.json"
    try:
        with open(filepath, "r") as f:
            status = json.load(f)
    except FileNotFoundError:
        print("No status data found.")
        return

    today = datetime.now().date()
    streak = {
        "journaled": 0,
        "planned": 0
    }

    for key in ["journaled", "planned"]:
        for i in range(30):  # Check up to 30 days back
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day not in status or not status[day].get(key):
                break
            streak[key] += 1

    print("\n🔥 CONSISTENCY STREAKS")
    print(f"📝 Journaled {streak['journaled']} days in a row")
    print(f"✅ Planned {streak['planned']} days in a row")
