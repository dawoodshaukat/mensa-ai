
# Add project root to sys.path for clean imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.reminders import check_streak_break, check_pending_tasks, check_inactivity, notify_user
 

import sys
import os
import json
import importlib.util
from datetime import datetime, timedelta

 
#   DYNAMIC PLANNER IMPORT

core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'core'))
planner_path = os.path.join(core_dir, 'planner.py')
spec = importlib.util.spec_from_file_location('planner', planner_path)
planner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(planner)
get_today_plan = planner.get_today_plan
add_or_update_today_plan = planner.add_or_update_today_plan
mark_today_tasks_done = planner.mark_today_tasks_done
get_weekly_summary = planner.get_weekly_summary
get_plan_by_date = planner.get_plan_by_date


#   COMMAND DESCRIPTIONS

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


#   STREAK CALCULATION

def get_combined_streak():
    """Calculate the streak of consecutive days with either a journal or plan entry."""
    memory_dir = os.path.join("memory")
    journal_path = os.path.join(memory_dir, "journal.json")
    plan_path = os.path.join(memory_dir, "daily_plan.json")
    dates = set()

    # Collect dates from journal
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

    # Collect dates from plan
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

    # Check for consecutive days
    while True:
        if current in dates:
            streak += 1
            current = current - timedelta(days=1)
        else:
            # If we missed today, warn only if there was activity before
            if streak == 0 and (current - timedelta(days=1)) in dates:
                missed = True
            break

    return streak, missed


#   JOURNAL COMMAND

def journal():
    """Prompt user for a journal entry and save it."""
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


#   PLAN COMMAND

def plan():
    """Prompt user for top 3 goals and save as today's plan."""
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


#   MAIN CLI ENTRY POINT

def main():
    # --- Reminder/Warning System ---
    memory_dir = os.path.join("memory")
    journal_path = os.path.join(memory_dir, "journal.json")
    plan_path = os.path.join(memory_dir, "daily_plan.json")
    warnings = []
    streak_warning = check_streak_break(get_combined_streak)
    if streak_warning:
        warnings.append(streak_warning)
    pending_warning = check_pending_tasks(get_today_plan)
    if pending_warning:
        warnings.append(pending_warning)
    inactivity_warning = check_inactivity(journal_path, plan_path)
    if inactivity_warning:
        warnings.append(inactivity_warning)
    for w in warnings:
        notify_user(w)
    """Main entry point for the Mensa CLI."""
    streak, missed = get_combined_streak()
    current_date = datetime.now()
    day_str = current_date.strftime('%A')
    date_str = current_date.strftime('%d %B %Y')
    print()
    print("👋 Welcome to Mensa AI — your mission-aligned assistant.")
    print(f"🔥 Current Streak: {streak} day{'s' if streak != 1 else ''}")
    if missed:
        print("⚠️ You missed a day! Your streak has been reset.")
    print(f"📆 Today: {day_str}, {date_str}")
    print()
    print("🛠️ Available Commands:")
    print("  ▶ start         – Set up or reset your session")
    print("  ▶ plan          – View or edit your upcoming plans")
    print("  ▶ plan today    – Add today’s top 3 priorities")
    print("  ▶ checkin       – Mark progress for today’s tasks")
    print("  ▶ streak        – View your streak status")
    print("  ▶ summary week  – Weekly performance snapshot")
    print("  ▶ journal       – Log your mood or reflections")
    print("  ▶ reminder      – View warnings or missed activity")
    print()

    # --- Command Input and Validation ---
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:]).strip().lower().replace("'", "").replace('"', "")
    else:
        command = input("Which command would you like to run?\n> ").strip().lower().replace("'", "").replace('"', "")

    # --- Help Command ---
    if command.startswith("help"):
        parts = command.split(" ", 1)
        if len(parts) == 2:
            help_cmd = parts[1].strip().lower()
            print(f"\n📝 {help_cmd} — {help_texts.get(help_cmd, 'No help found for that command.')}\n")
        else:
            print("\n🆘 Usage: help <command>\nExample: help checkin\n")
        return

    # --- Command Validation ---
    valid_commands = [
        "start", "plan", "plan today", "checkin",
        "streak", "summary week", "journal", "help", "reminder"
    ]
    if command not in valid_commands:
        print("⚠️ Unknown command. Try one of:", ", ".join(valid_commands))
        return

    # --- Command Execution ---
    if command == "journal":
        journal()
    elif command == "plan":
        plan()
    elif command == "streak":
        streak, missed = get_combined_streak()
        print(f"🔥 Your streak: {streak}")
        if missed:
            print("⚠️ You missed a day! Your streak has been reset.")
    elif command.startswith("plan today"):
        # Flags
        edit = "--edit" in command
        view = "--view" in command
        today_plan = get_today_plan()
        if view:
            if today_plan:
                print(f"Today's plan: {today_plan['tasks']}")
            else:
                print("No plan for today.")
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
                parts = raw.split('#', 1)
                task = parts[0].strip()
                tag = parts[1].strip()
            else:
                task = raw
                tag = ""
            tasks.append({"task": task, "tag": tag, "done": False})
        add_or_update_today_plan(tasks)
        print("✅ Today's plan saved.")
    elif command == "checkin":
        today_plan = get_today_plan()
        if not today_plan or not today_plan['tasks']:
            print("⚠️ No plan found for today. Use 'plan today' to create one.")
            return
        done_list = []
        for t in today_plan['tasks']:
            ans = input(f"Did you complete '{t['task']}'? (y/n): ").strip().lower()
            done_list.append(ans == 'y')
        mark_today_tasks_done(done_list)
        if all(done_list):
            print("✅ All tasks complete! Streak updated.")
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
        # Show all current warnings
        if not warnings:
            print("✅ No reminders or warnings. You're on track!")
        else:
            print("🔔 Reminders & Warnings:")
            for w in warnings:
                print(w)
    elif command == "start":
        print("Session setup/reset is not yet implemented.")
    else:
        print("⚠️ Unknown command. Type 'help <command>' for help.")

if __name__ == "__main__":
    main()