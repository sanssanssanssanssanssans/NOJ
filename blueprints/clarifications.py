from flask import Blueprint, render_template, request, redirect, session
from models import get_contest, get_clarifications, save_clarifications
from storage import now_ts
import uuid

bp = Blueprint("clarifications", __name__)

@bp.route("/clarifications/<cid>", methods=["GET","POST"])
def clarifications(cid):
    c=get_contest(cid)
    if not c: return "Contest not found",404
    if c.get("is_private"):
        u=session.get("user")
        if not u or (u["username"] not in c.get("whitelist",[]) and (request.args.get("invite")!=c.get("invite_code",""))):
            return render_template("contest_locked.html", contest=c)
    cls=get_clarifications()
    if request.method=="POST":
        if "user" not in session: return "Login required",401
        q=request.form["question"].strip()
        if not q: return redirect(f"/clarifications/{cid}")
        cls.append({"id":uuid.uuid4().hex[:8],"contest_id":cid,"user":session["user"]["username"],"question":q,"answer":"","at":now_ts()})
        save_clarifications(cls)
        return redirect(f"/clarifications/{cid}")
    items=[x for x in cls if x["contest_id"]==cid]
    return render_template("clarifications.html", contest=c, items=items, user=session.get("user"))

@bp.route("/clarifications/<cid>/answer/<qid>", methods=["POST"])
def clarifications_answer(cid,qid):
    if "user" not in session or not session["user"].get("is_admin"): return "Forbidden",403
    cls=get_clarifications()
    for x in cls:
        if x["id"]==qid and x["contest_id"]==cid:
            x["answer"]=request.form.get("answer","").strip()
    save_clarifications(cls)
    return redirect(f"/clarifications/{cid}")
