import os
import json
from datetime import datetime
import sys

# Fix Python path so it can find modules from root
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.modules.weekly import weekly_report


def journal():
    entry = input("📝 What's on your mind today?\n> ").strip()
    if not entry:
        print("⚠️ No entry written.")
        return

    filepath = os.path.join(BASE_DIR, "memory", "journal.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
    else:
        data = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data.append({"timestamp": timestamp, "entry": entry})

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Journal entry saved.")


def plan():
    goals = []
    print("🧠 What are your 3 priorities for today?")
    for i in range(3):
        goal = input(f"{i+1}. ").strip()
        if goal:
            goals.append(goal)

    filepath = os.path.join(BASE_DIR, "memory", "daily_plan.json")
    with open(filepath, "w") as f:
        json.dump({"goals": goals}, f, indent=2)

    print("✅ Plan saved.")


def review():
    today = datetime.now().strftime("%Y-%m-%d")

    # Load plan
    try:
        with open(os.path.join(BASE_DIR, "memory", "daily_plan.json"), "r") as f:
            plan = json.load(f)
    except FileNotFoundError:
        plan = {"goals": []}

    # Load journal
    try:
        with open(os.path.join(BASE_DIR, "memory", "journal.json"), "r") as f:
            journals = json.load(f)
            todays_entries = [j for j in journals if j["timestamp"].startswith(today)]
    except FileNotFoundError:
        todays_entries = []

    # Load mission
    try:
        with open(os.path.join(BASE_DIR, "mission.txt"), "r") as f:
            mission = f.read().strip()
    except FileNotFoundError:
        mission = "(Mission not defined)"

    print("\n🧠 MISSION")
    print(f"> {mission}")

    print("\n✅ PLAN FOR TODAY")
    for i, g in enumerate(plan.get("goals", []), 1):
        print(f"{i}. {g}")

    print("\n📝 TODAY'S JOURNAL ENTRIES")
    if todays_entries:
        for j in todays_entries:
            print(f"- {j['timestamp']}: {j['entry']}")
    else:
        print("- No journal entries found.")

    journaled = bool(todays_entries)
    planned = bool(plan.get("goals"))

    status_file = os.path.join(BASE_DIR, "memory", "status.json")
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            status = json.load(f)
    else:
        status = {}

    status[today] = {
        "journaled": journaled,
        "planned": planned
    }

    with open(status_file, "w") as f:
        json.dump(status, f, indent=2)

    print("\n📊 STATUS UPDATED")
    print(f"> Journaled: {journaled}, Planned: {planned}")


def main():
    print("Welcome to Mensa AI — your mission-aligned assistant.")
    print("Available commands: start | plan | journal | review | weekly")

    command = input("\nWhich command would you like to run?\n> ").strip().lower()

    if command == "journal":
        journal()
    elif command == "plan":
        plan()
    elif command == "review":
        review()
    elif command == "weekly":
        weekly_report()
    else:
        print("⚠️ Unknown command. Try again.")


if __name__ == "__main__":
    main()

