from flask import Blueprint, render_template, request, redirect, session, abort
import uuid
from models import get_announcements, save_announcements
from storage import now_ts

bp = Blueprint("announcements", __name__)

def admin_required():
    u=session.get("user")
    if not u or not u.get("is_admin"): abort(403)

@bp.route("/announcements")
def list_ann():
    items=get_announcements()
    items.sort(key=lambda x: x.get("created_at",""), reverse=True)
    return render_template("announcements.html", items=items, user=session.get("user"))

@bp.route("/admin/announcement/new", methods=["GET","POST"])
def new_ann():
    admin_required()
    if request.method=="POST":
        title=request.form.get("title","").strip()
        body=request.form.get("body","").strip()
        if not title or not body: return "Title and body required",400
        items=get_announcements()
        items.append({"id":uuid.uuid4().hex[:8],"title":title,"body":body,"created_at":now_ts(),"author":session["user"]["username"]})
        save_announcements(items)
        return redirect("/announcements")
    return render_template("announcement_new.html")
