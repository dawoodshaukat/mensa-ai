"""
Reminder and warning utilities for Mensa CLI.
"""
import os
import json
from datetime import datetime, timedelta

def check_streak_break(get_combined_streak):
    """Return a warning if the user broke their journaling or check-in streak."""
    streak, missed = get_combined_streak()
    if missed:
        return "⚠️ You broke your streak! Try to keep it going."
    if streak == 0:
        return "⚠️ No active streak. Start journaling or checking in!"
    return None

def check_pending_tasks(get_today_plan):
    """Return a warning if there are incomplete tasks in today's plan."""
    today_plan = get_today_plan()
    if today_plan and today_plan.get('tasks'):
        incomplete = [t for t in today_plan['tasks'] if not t.get('done')]
        if incomplete:
            return f"⚠️ You have {len(incomplete)} incomplete task(s) in your daily plan."
    return None

def check_inactivity(journal_path, plan_path):
    """Return a warning if it's been 24h since last journal or check-in."""
    now = datetime.now()
    last_activity = None
    # Check last journal
    if os.path.exists(journal_path):
        try:
            with open(journal_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                last_journal = max(datetime.strptime(e['timestamp'], "%Y-%m-%d %H:%M:%S") for e in data if 'timestamp' in e)
                last_activity = last_journal
        except Exception:
            pass
    # Check last plan check-in
    if os.path.exists(plan_path):
        try:
            with open(plan_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data:
                last_plan = max(datetime.strptime(e['date'], "%Y-%m-%d") for e in data if 'date' in e)
                if not last_activity or last_plan > last_activity:
                    last_activity = last_plan
        except Exception:
            pass
    if last_activity and (now - last_activity) > timedelta(hours=24):
        return "⚠️ It's been over 24 hours since your last check-in or journal entry."
    return None

def notify_user(message):
    """Print a notification message to the user."""
    if message:
        print(message)
