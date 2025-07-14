import os
import json
from datetime import datetime

def journal():
    entry = input("📝 What's on your mind today?\n> ")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    journal_entry = {
        "timestamp": timestamp,
        "entry": entry
    }

    filepath = "memory/journal.json"
    os.makedirs("memory", exist_ok=True)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(journal_entry)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ Journal entry saved.")

def plan():
    print("📅 Let's set your top 3 goals for today.")
    goals = []
    for i in range(1, 4):
        goal = input(f"Goal {i}: ")
        goals.append(goal)

    plan_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "goals": goals
    }

    filepath = "memory/daily_plan.json"
    os.makedirs("memory", exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(plan_entry, f, indent=2)

    print("✅ Today's plan saved.")

def main():
    print("Welcome to Mensa AI — your mission-aligned assistant.")
    print("Available commands: start | plan | journal")

    command = input("\nWhich command would you like to run?\n> ").strip().lower()

    if command == "journal":
        journal()
    elif command == "plan":
        plan()
    else:
        print("⚠️ Unknown command. Try 'journal' or 'plan'.")

if __name__ == "__main__":
    main()
