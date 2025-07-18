# --- Add sys.path for absolute 'src' imports ---
import sys
import os
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# --- src module imports ---
from src.utils.reminders import check_streak_break, check_pending_tasks, check_inactivity, notify_user
from src.core.session import (
    load_session,
    save_session,
    update_last_active,
    update_streak,
    update_today_plan
)
from src.core.planner import (
    get_today_plan,
    add_or_update_today_plan,
    mark_today_tasks_done,
    get_weekly_summary
)

help_texts = {
    "start": "Initialize or reset your Mensa session.",
    "plan": "View or edit your upcoming plans.",
    "plan today": "Add your top 3 priorities for today.",
    "checkin": "Mark which of today's tasks you completed.",
    "streak": "Check your current streak status.",
    "summary week": "View your weekly performance snapshot.",
    "journal": "Log your mood, thoughts, or reflections.",
    "help": "Usage: help <command> — Show help for a specific command."
}

def get_combined_streak():
    memory_dir = os.path.join("memory")
    journal_path = os.path.join(memory_dir, "journal.json")
    plan_path = os.path.join(memory_dir, "daily_plan.json")
    dates = set()

    if os.path.exists(journal_path):
        try:
            with open(journal_path, "r", encoding="utf-8") as f:
                journal_data = json.load(f)
            for entry in journal_data:
                ts = entry.get("timestamp", "")
                if ts:
                    try:
                        d = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date()
                        dates.add(d)
                    except Exception:
                        pass
        except Exception:
            pass

    if os.path.exists(plan_path):
        try:
            with open(plan_path, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
            for entry in plan_data:
                dstr = entry.get("date", "")
                if dstr:
                    try:
                        d = datetime.strptime(dstr, "%Y-%m-%d").date()
                        dates.add(d)
                    except Exception:
                        pass
        except Exception:
            pass

    if not dates:
        return 0, False

    today = datetime.now().date()
    streak = 0
    missed = False
    current = today

    while True:
        if current in dates:
            streak += 1
            current -= timedelta(days=1)
        else:
            if streak == 0 and (current - timedelta(days=1)) in dates:
                missed = True
            break

    return streak, missed

def journal():
    entry = input("📝 What's on your mind today?\n> ")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    journal_entry = {
        "timestamp": timestamp,
        "entry": entry
    }
    memory_dir = os.path.join("memory")
    filepath = os.path.join(memory_dir, "journal.json")
    os.makedirs(memory_dir, exist_ok=True)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []
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
    memory_dir = os.path.join("memory")
    filepath = os.path.join(memory_dir, "daily_plan.json")
    os.makedirs(memory_dir, exist_ok=True)
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            data = []
    else:
        data = []
    data.append(plan_entry)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("✅ Today's plan saved.")

def main():
    warnings = notify_user()
    for w in warnings:
        print(w)

    streak, missed = get_combined_streak()
    current_date = datetime.now()
    print("\n👋 Welcome to Mensa AI — your mission-aligned assistant.")
    print(f"🔥 Current Streak: {streak} day{'s' if streak != 1 else ''}")
    if missed:
        print("⚠️ You missed a day! Your streak has been reset.")
    print(f"📆 Today: {current_date.strftime('%A')}, {current_date.strftime('%d %B %Y')}")
    print("\n🛠️ Available Commands:")
    for cmd in help_texts:
        print(f"  ▶ {cmd}")

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:]).strip().lower().replace("'", "").replace('"', "")
    else:
        command = input("Which command would you like to run?\n> ").strip().lower().replace("'", "").replace('"', "")

    if command.startswith("help"):
        parts = command.split(" ", 1)
        if len(parts) == 2:
            help_cmd = parts[1].strip().lower()
            print(f"\n📝 {help_cmd} — {help_texts.get(help_cmd, 'No help found for that command.')}\n")
        else:
            print("\n🆘 Usage: help <command>\nExample: help checkin\n")
        return

    if command not in help_texts:
        print("⚠️ Unknown command. Try one of:", ", ".join(help_texts))
        return

    if command == "journal":
        journal()
    elif command == "plan":
        plan()
    elif command == "streak":
        s, missed = get_combined_streak()
        print(f"🔥 Your streak: {s}")
        if missed:
            print("⚠️ You missed a day! Your streak has been reset.")
    elif command.startswith("plan today"):
        edit = "--edit" in command
        view = "--view" in command
        today_plan = get_today_plan()
        if view:
            print("Today's plan:", today_plan['tasks'] if today_plan else "No plan.")
            return
        if today_plan and not edit:
            print("Plan for today already exists. Use --edit to modify or --view to see it.")
            return
        print("Let's set your top 3 tasks for today. Use #tag for optional tags (e.g., Workout #health)")
        tasks = []
        for i in range(1, 4):
            raw = input(f"Task {i}: ").strip()
            if not raw:
                continue
            if '#' in raw:
                task, tag = map(str.strip, raw.split('#', 1))
            else:
                task, tag = raw, ""
            tasks.append({"task": task, "tag": tag, "done": False})
        add_or_update_today_plan(tasks)
        update_today_plan({"tasks": tasks})
        update_last_active()
        print("✅ Today's plan saved.")
    elif command == "checkin":
        today_plan = get_today_plan()
        if not today_plan or not today_plan['tasks']:
            print("⚠️ No plan found for today. Use 'plan today' to create one.")
            return
        done_list = [input(f"Did you complete '{t['task']}'? (y/n): ").strip().lower() == 'y' for t in today_plan['tasks']]
        mark_today_tasks_done(done_list)
        if all(done_list):
            print("✅ All tasks complete! Streak updated.")
            update_last_active()
            session = load_session()
            new_streak = session.get("streak", 0) + 1
            update_streak(new_streak)
        else:
            print("⚠️ Not all tasks complete. Keep going!")
    elif command == "summary week":
        summary, active_days = get_weekly_summary()
        print("Weekly Summary:")
        for day in summary:
            d = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a')
            if day['total'] == 0:
                print(f"{d}: no plan ❌")
            else:
                check = '✅' if day['done'] == day['total'] else '⚠️'
                print(f"{d}: {day['done']}/{day['total']} {check}")
        print(f"{active_days} active day{'s' if active_days != 1 else ''} this week.")
    elif command == "reminder":
        if not warnings:
            print("✅ No reminders or warnings. You're on track!")
        else:
            print("🔔 Reminders & Warnings:")
            for w in warnings:
                print(w)
    elif command == "start":
        print("Session setup/reset is not yet implemented.")

if __name__ == "__main__":
    main()
