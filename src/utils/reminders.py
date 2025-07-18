# Add sys.path modification at the very top for src imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

"""
reminders.py - Modular Reminder/Warning System for Mensa AI CLI

Provides functions to check for streak breaks, pending tasks, and inactivity.
Uses session data for robust, user-centric reminders.
"""

from datetime import datetime
from src.core.session import load_session

def check_streak_break():
    session = load_session()
    streak = session.get('streak', 0)
    last_active = session.get('last_active')
    if not last_active:
        return None
    last_date = datetime.strptime(last_active, "%Y-%m-%d")
    today = datetime.now().date()
    days_diff = (today - last_date.date()).days
    if days_diff == 1:
        return f"⚠️ You are about to break your streak! Last activity was yesterday. Current streak: {streak} days."
    elif days_diff > 1:
        return f"❌ Streak broken! Last activity was {days_diff} days ago. Your streak has been reset."
    return None

def check_pending_tasks():
    session = load_session()
    today_plan = session.get('today_plan', {})
    tasks = today_plan.get('tasks', [])
    if not tasks:
        return None
    incomplete = [t for t in tasks if not t.get('done')]
    if incomplete:
        return f"⏳ You have {len(incomplete)} incomplete task(s) for today. Don't forget to check in!"
    return None

def check_inactivity():
    session = load_session()
    last_active = session.get('last_active')
    if not last_active:
        return "⚠️ No activity detected yet. Start your first session!"
    last_date = datetime.strptime(last_active, "%Y-%m-%d")
    today = datetime.now().date()
    days_diff = (today - last_date.date()).days
    if days_diff > 1:
        return f"🔕 You have been inactive for {days_diff} days. Let's get back on track!"
    return None

def notify_user():
    warnings = []
    for fn in (check_streak_break, check_pending_tasks, check_inactivity):
        msg = fn()
        if msg:
            warnings.append(msg)
    return warnings
