import os
import json
from datetime import datetime, timedelta

PLANNER_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'planner.json')

def load_plans():
    if not os.path.exists(PLANNER_PATH):
        return []
    try:
        with open(PLANNER_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_plans(plans):
    os.makedirs(os.path.dirname(PLANNER_PATH), exist_ok=True)
    with open(PLANNER_PATH, 'w', encoding='utf-8') as f:
        json.dump(plans, f, indent=2)

def get_today_plan():
    today = datetime.now().strftime('%Y-%m-%d')
    plans = load_plans()
    for plan in plans:
        if plan['date'] == today:
            return plan
    return None

def add_or_update_today_plan(tasks):
    today = datetime.now().strftime('%Y-%m-%d')
    plans = load_plans()
    for plan in plans:
        if plan['date'] == today:
            plan['tasks'] = tasks
            save_plans(plans)
            return
    plans.append({'date': today, 'tasks': tasks})
    save_plans(plans)

def mark_today_tasks_done(done_list):
    today = datetime.now().strftime('%Y-%m-%d')
    plans = load_plans()
    for plan in plans:
        if plan['date'] == today:
            for idx, done in enumerate(done_list):
                plan['tasks'][idx]['done'] = done
            save_plans(plans)
            return

def get_weekly_summary():
    plans = load_plans()
    today = datetime.now().date()
    week = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    summary = []
    active_days = 0
    for d in week:
        plan = next((p for p in plans if p['date'] == d), None)
        if plan:
            total = len(plan['tasks'])
            done = sum(1 for t in plan['tasks'] if t.get('done'))
            summary.append({'date': d, 'done': done, 'total': total})
            if total > 0:
                active_days += 1
        else:
            summary.append({'date': d, 'done': 0, 'total': 0})
    return summary, active_days

def get_plan_by_date(date):
    plans = load_plans()
    for plan in plans:
        if plan['date'] == date:
            return plan
    return None
