from flask import Blueprint, render_template, request, redirect, url_for, session, abort
import os, uuid, zipfile, shutil, math
from models import get_problems, save_problems, get_problem, get_contests, get_contest
from judge import collect_io_pairs
import markdown
from storage import now_ts

bp = Blueprint("problems", __name__)

def admin_required():
    u=session.get("user")
    if not u or not u.get("is_admin"): abort(403)

@bp.route("/admin_panel")
def admin_panel():
    admin_required()
    from models import get_submissions, get_problems
    subs = get_submissions()
    problems = get_problems()
    # contests 제거
    return render_template(
        "admin_panel.html",
        user=session.get("user"),
        submissions=subs,
        problems=problems,
    )

@bp.route("/admin/problem/new", methods=["GET","POST"])
def admin_problem_new():
    admin_required()
    if request.method=="POST":
        ps=get_problems()
        pid=str(uuid.uuid4())[:8]
        title=request.form["title"]
        description=request.form.get("description","")
        time_limit=request.form.get("time_limit","2")
        memory_limit=request.form.get("memory_limit","256")
        cmp_mode=request.form.get("cmp_mode","exact")
        spj_flag=request.form.get("spj","off")=="on"
        visibility=request.form.get("visibility","public")
        ps.append({
            "id":pid,"title":title,"description":description,
            "time_limit":time_limit,"memory_limit":memory_limit,
            "cmp":cmp_mode,"spj":spj_flag,"tc_version":1,
            "created_at":now_ts(),"views":0,"visibility":visibility
        })
        save_problems(ps)
        if "zipfile" in request.files and request.files["zipfile"].filename:
            z=request.files["zipfile"]
            ep=f"testcases/{pid}/v1"
            os.makedirs(ep,exist_ok=True)
            with zipfile.ZipFile(z,'r') as zf: zf.extractall(ep)
            if not collect_io_pairs(ep):
                shutil.rmtree(ep,ignore_errors=True)
                return "Invalid testcase ZIP: no .in/.out pairs found.",400
        return redirect(url_for("problems.problem", pid=pid))
    return render_template("admin.html")

@bp.route("/admin/problem/<pid>/edit", methods=["GET","POST"])
def admin_problem_edit(pid):
    admin_required()
    ps=get_problems()
    p=next((x for x in ps if x["id"]==pid),None)
    if not p: return "Not found",404
    if request.method=="POST":
        p["title"]=request.form.get("title",p["title"])
        p["description"]=request.form.get("description",p["description"])
        p["time_limit"]=request.form.get("time_limit",p["time_limit"])
        p["memory_limit"]=request.form.get("memory_limit",p["memory_limit"])
        p["cmp"]=request.form.get("cmp_mode",p.get("cmp","exact"))
        p["spj"]=request.form.get("spj","off")=="on"
        p["visibility"]=request.form.get("visibility",p.get("visibility","public"))
        if "zipfile" in request.files and request.files["zipfile"].filename:
            p["tc_version"]=int(p.get("tc_version",1))+1
            ep=f"testcases/{pid}/v{p['tc_version']}"
            os.makedirs(ep,exist_ok=True)
            with zipfile.ZipFile(request.files["zipfile"],'r') as zf: zf.extractall(ep)
            if not collect_io_pairs(ep):
                shutil.rmtree(ep,ignore_errors=True)
                return "Invalid testcase ZIP: no .in/.out pairs found.",400
        save_problems(ps)
        return redirect(url_for("problems.problem", pid=pid))
    return render_template("admin_edit_problem.html", p=p)

def _is_visible_to_user(p, contest_context_id=None):
    vis = p.get("visibility","public")
    if vis=="public": return True
    if vis=="contest_only":
        return bool(contest_context_id)
    if vis=="after_contest":
        if not contest_context_id: return False
        c=get_contest(contest_context_id)
        if not c: return False
        from models import parse_ts
        t_end = parse_ts(c.get("end","")); from storage import now_ts as _now
        t_now = parse_ts(_now())
        return bool(t_end and t_now and t_now>=t_end)
    return True

@bp.route("/problem/<pid>")
def problem(pid):
    p=get_problem(pid)
    if not p: return "Problem not found",404
    cid=request.args.get("contest_id")
    if cid:
        session["current_contest"] = cid
    if not _is_visible_to_user(p, cid):
        return render_template("contest_locked.html", contest={"title":"Locked problem"})
    ps=get_problems()
    for i,x in enumerate(ps):
        if x["id"]==pid:
            x["views"]=int(x.get("views",0))+1
            ps[i]=x
            break
    save_problems(ps)
    return render_template("problem.html", p=p, description_html=markdown.markdown(p.get("description","")))

@bp.route("/problems")
def problems_list():
    q = (request.args.get("q") or "").strip().lower()
    page = max(1, int(request.args.get("page", "1")))
    per_page = 10
    allp = get_problems()
    filt=[]
    for p in allp:
        if q and q not in p.get("title","").lower(): continue
        if p.get("visibility","public")!="public": continue
        filt.append(p)
    filt.sort(key=lambda x: x.get("created_at",""), reverse=True)
    total=len(filt)
    pages=max(1, math.ceil(total/per_page))
    start=(page-1)*per_page
    items=filt[start:start+per_page]
    return render_template("problems_list.html", items=items, page=page, pages=pages, q=q, total=total)

@bp.route("/admin", methods=["GET","POST"])
def admin_legacy():
    return admin_problem_new()
