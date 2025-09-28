from flask import Blueprint, render_template, session
from models import get_users, get_submissions
from datetime import datetime

bp = Blueprint("ranking", __name__)

def _parse(ts):
    try: return datetime.fromisoformat(ts)
    except: return None

@bp.route("/ranking")
def ranking():
    users = get_users()
    subs = get_submissions()

    solved = {}
    last_ac = {}

    for s in subs:
        if s.get("result") != "AC": 
            continue
        u = s.get("username")
        pid = s.get("problem_id")
        if not u or not pid: 
            continue
        solved.setdefault(u, set()).add(pid)
        t = _parse(s.get("timestamp",""))
        if t:
            last_ac[u] = t if (u not in last_ac or t > last_ac[u]) else last_ac[u]

    rows = []
    for u in users:
        name = u.get("username")
        sc = len(solved.get(name, set()))
        rows.append({
            "username": name,
            "solved_count": sc,
            "last_ac": last_ac.get(name),
            "is_admin": bool(u.get("is_admin",False)),
        })

    rows.sort(key=lambda r: (-r["solved_count"],
                             r["last_ac"] or datetime.max,
                             r["username"]))
    return render_template("ranking.html", rows=rows, user=session.get("user"))

@bp.route("/user/<username>")
def user_profile(username):
    users = get_users()
    u = next((x for x in users if x["username"]==username), None)
    if not u: 
        return "User not found", 404
    subs = get_submissions()
    mine = [s for s in subs if s.get("username")==username]
    mine.sort(key=lambda s: s.get("timestamp",""), reverse=True)
    recent = mine[:50]
    unique_ac = len({s["problem_id"] for s in mine if s.get("result")=="AC"})
    return render_template("profile.html", u={**u, "solved_count": unique_ac}, recent=recent, user=session.get("user"))
