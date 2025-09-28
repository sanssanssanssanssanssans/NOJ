from flask import Blueprint, render_template, session
from models import get_users, get_submissions

bp = Blueprint("ranking", __name__)

@bp.route("/ranking")
def ranking():
    users=get_users()
    rows=[]
    for u in users:
        rows.append({"username":u["username"],"rating":int(u.get("rating",1500)),"contests":int(u.get("contests",0)),"is_admin":bool(u.get("is_admin",False))})
    rows.sort(key=lambda x:(-x["rating"],-x["contests"],x["username"]))
    return render_template("ranking.html", rows=rows, user=session.get("user"))

@bp.route("/user/<username>")
def user_profile(username):
    users=get_users()
    u=next((x for x in users if x["username"]==username), None)
    if not u: return "User not found",404
    subs=get_submissions()
    recent=[s for s in subs if s.get("username")==username]
    recent.sort(key=lambda s:s.get("timestamp",""), reverse=True)
    recent=recent[:50]
    return render_template("profile.html", u=u, recent=recent, user=session.get("user"))
