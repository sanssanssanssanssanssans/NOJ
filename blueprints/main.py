from flask import Blueprint, render_template, session
from models import get_problems, get_contests, get_submissions, get_announcements

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    problems=[{**p,"cmp":p.get("cmp","exact"),"spj":p.get("spj",False)} for p in get_problems()]
    public_recent=[p for p in problems if p.get("visibility","public")=="public"]
    public_recent.sort(key=lambda x:x.get("created_at",""), reverse=True)
    recent=public_recent[:10]
    announcements=get_announcements()
    announcements.sort(key=lambda x:x.get("created_at",""), reverse=True)
    contests=get_contests()
    return render_template("index.html", problems=problems, recent=recent, announcements=announcements[:5], contests=contests, user=session.get("user"))

@bp.route("/status")
def status():
    return render_template("status.html", submissions=get_submissions())
