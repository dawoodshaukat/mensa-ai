import os
import json
from datetime import datetime

SESSION_PATH = os.path.join(os.path.dirname(__file__), 'session_data.json')

def load_session():
    if not os.path.exists(SESSION_PATH):
        return {
            "streak": 0,
            "last_active": None,
            "today_plan": {}
        }
    try:
        with open(SESSION_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {
            "streak": 0,
            "last_active": None,
            "today_plan": {}
        }

def save_session(data):
    with open(SESSION_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def update_last_active():
    session = load_session()
    session['last_active'] = datetime.now().strftime('%Y-%m-%d')
    save_session(session)

def update_streak(streak_value):
    session = load_session()
    session['streak'] = streak_value
    save_session(session)

def update_today_plan(plan):
    session = load_session()
    session['today_plan'] = plan
    save_session(session)

if __name__ == "__main__":
    print("🔁 Testing session system...")
    data = load_session()
    print("Loaded session:", data)
    update_last_active()
    update_streak(3)
    update_today_plan({"tasks": [{"task": "test", "done": False}]})
    print("✅ Session updated.")
