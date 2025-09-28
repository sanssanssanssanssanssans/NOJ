from flask import Blueprint, render_template, request, redirect, session
import uuid
from storage import now_ts
from models import get_board, save_board

bp = Blueprint("board", __name__)

@bp.route("/board", methods=["GET"])
def board_list():
    items=get_board()
    items.sort(key=lambda x: x.get("updated_at", x.get("created_at","")), reverse=True)
    return render_template("board_list.html", items=items, user=session.get("user"))

@bp.route("/board/new", methods=["GET","POST"])
def board_new():
    if request.method=="GET":
        if "user" not in session: return redirect("/login")
        return render_template("board_new.html", user=session.get("user"))
    if "user" not in session: return "Login required", 401
    title=request.form.get("title","").strip()
    body=request.form.get("body","").strip()
    tag=request.form.get("tag","").strip()
    ref_problem=request.form.get("problem_id","").strip()
    ref_contest=request.form.get("contest_id","").strip()
    if not title or not body: return "Title and body required", 400
    items=get_board()
    tid=str(uuid.uuid4())[:8]
    now=now_ts()
    items.append({"id":tid,"title":title,"body":body,"user":session["user"]["username"],"tag":tag,"problem_id":ref_problem,"contest_id":ref_contest,"created_at":now,"updated_at":now,"replies":[]})
    save_board(items)
    return redirect(f"/board/{tid}")

@bp.route("/board/<tid>", methods=["GET","POST"])
def board_thread(tid):
    items=get_board()
    t=next((x for x in items if x["id"]==tid), None)
    if not t: return "Thread not found",404
    if request.method=="POST":
        if "user" not in session: return "Login required",401
        reply=request.form.get("reply","").strip()
        if not reply: return redirect(f"/board/{tid}")
        t["replies"].append({"user":session["user"]["username"],"body":reply,"at":now_ts()})
        t["updated_at"]=now_ts()
        save_board(items)
        return redirect(f"/board/{tid}")
    return render_template("board_thread.html", t=t, user=session.get("user"))
