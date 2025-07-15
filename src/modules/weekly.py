import json
from datetime import datetime, timedelta

def weekly_report():
    filepath = "memory/status.json"
    try:
        with open(filepath, "r") as f:
            status = json.load(f)
    except FileNotFoundError:
        print("No status file found.")
        return

    today = datetime.now().date()
    journal_count = 0
    plan_count = 0
    total_days = 0

    print("\n📊 WEEKLY REPORT (Last 7 Days)")

    for i in range(7):
        day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        if day in status:
            total_days += 1
            journaled = status[day].get("journaled", False)
            planned = status[day].get("planned", False)

            if journaled:
                journal_count += 1
            if planned:
                plan_count += 1

            print(f"{day} - 📝 Journaled: {journaled}, ✅ Planned: {planned}")
        else:
            print(f"{day} - No data")

    if total_days == 0:
        print("\nNo activity tracked this week.")
        return

    print("\n📈 SUMMARY")
    print(f"📝 Journaled {journal_count} out of {total_days} days")
    print(f"✅ Planned {plan_count} out of {total_days} days")
