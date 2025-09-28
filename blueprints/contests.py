from flask import Blueprint, render_template, request, redirect, session, abort, url_for
import uuid, secrets, datetime
from models import get_contests, save_contests, get_contest, get_problem, get_problems
from models import get_submissions, in_window, parse_ts

bp = Blueprint("contests", __name__)

def admin_required():
    u = session.get("user")
    if not u or not u.get("is_admin"):
        abort(403)

@bp.route("/contests")
def contests_list():
    return render_template("contests.html", contests=get_contests(), user=session.get("user"))

@bp.route("/contest_admin", methods=["GET","POST"])
def contest_admin():
    admin_required()
    if request.method=="POST":
        cs=get_contests()
        cid=str(uuid.uuid4())[:8]
        title=request.form["title"]
        start=request.form["start"]
        end=request.form["end"]
        penalty=int(request.form.get("penalty","20"))
        problem_ids=[s.strip() for s in request.form.get("problem_ids","").split(",") if s.strip()]
        is_private=request.form.get("is_private","off")=="on"
        invite_code=secrets.token_urlsafe(6) if is_private else ""
        freeze_min=int(request.form.get("freeze_min","0"))
        whitelist=[s.strip() for s in request.form.get("whitelist","").split(",") if s.strip()]
        cs.append({"id":cid,"title":title,"start":start,"end":end,"penalty":penalty,"problems":problem_ids,"is_private":is_private,"invite_code":invite_code,"whitelist":whitelist,"freeze_min":freeze_min})
        save_contests(cs)
        return redirect(f"/contest/{cid}")
    from models import get_problems
    return render_template("contest_admin.html", problems=get_problems(), contests=get_contests())

@bp.route("/contest/<cid>", methods=["GET","POST"])
def contest_view(cid):
    session["current_contest"] = cid
    c=get_contest(cid)
    if not c: return "Contest not found",404
    session["current_contest"] = cid
    if c.get("is_private"):
        u=session.get("user")
        allowed=False
        if u and (u["username"] in c.get("whitelist",[])): allowed=True
        elif u and request.args.get("invite")==c.get("invite_code",""): allowed=True
        if not allowed: return render_template("contest_locked.html", contest=c)
    ps=[get_problem(pid) for pid in c.get("problems",[])]
    return render_template("contest.html", contest=c, problems=ps, user=session.get("user"))

@bp.route("/contest/<cid>/standings_debug")
def contest_standings_debug(cid):
    from flask import jsonify
    c = get_contest(cid)
    if not c: return "Contest not found", 404
    subs = get_submissions()
    window = [x for x in subs if x.get("contest_id")==cid and in_window(x["timestamp"], c["start"], c["end"])]
    return jsonify({
        "contest": {"id": c["id"], "start": c["start"], "end": c["end"]},
        "window_count": len(window),
        "window_samples": window[-10:],
        "all_recent_samples": subs[-10:],
    })

@bp.route("/contest/<cid>/join", methods=["POST"])
def contest_join(cid):
    if "user" not in session: abort(401)
    c=get_contest(cid)
    if not c: return "Contest not found",404
    code=request.form.get("invite","")
    u=session["user"]["username"]
    if c.get("is_private"):
        if u in c.get("whitelist",[]) or code==c.get("invite_code",""):
            if u not in c["whitelist"]:
                cs=get_contests()
                for i,x in enumerate(cs):
                    if x["id"]==cid:
                        cs[i]["whitelist"].append(u)
                save_contests(cs)
            return redirect(f"/contest/{cid}")
        return "Invalid invite",403
    return redirect(f"/contest/{cid}")

def compute_standings(contest):
    subs=get_submissions()
    s=parse_ts(contest["start"]); e=parse_ts(contest["end"]); f=contest.get("freeze_min",0)
    freeze_at=e-datetime.timedelta(minutes=f) if f and e else None
    window=[x for x in subs if x.get("contest_id")==contest["id"] and in_window(x["timestamp"],contest["start"],contest["end"])]
    probs=contest.get("problems",[])
    S={}
    for x in window:
        u=x["username"]; pid=x["problem_id"]
        if u not in S: S[u]={"solved":0,"penalty":0,"detail":{p:{"tries":0,"time":None,"ac":False,"frozen":False} for p in probs}}
        d=S[u]["detail"].get(pid)
        if not d: continue
        t=parse_ts(x["timestamp"])
        is_frozen=bool(freeze_at and t and t>=freeze_at)
        if d["ac"]:
            if is_frozen: d["frozen"]=True
            continue
        d["tries"]+=1
        if x["result"]=="AC":
            d["ac"]=True
            minutes=int((t-s).total_seconds()//60) if t and s else 0
            d["time"]=minutes
            if freeze_at and t and t>=freeze_at: d["frozen"]=True
            if not d["frozen"]:
                S[u]["solved"]+=1
                S[u]["penalty"]+=minutes+contest.get("penalty",20)*(d["tries"]-1)
    rank=[]
    for u,v in S.items(): rank.append({"username":u,"solved":v["solved"],"penalty":v["penalty"],"detail":v["detail"]})
    rank.sort(key=lambda x:(-x["solved"],x["penalty"],x["username"]))
    return rank

@bp.route("/contest/<cid>/standings")
def contest_standings(cid):
    c=get_contest(cid)
    if not c: return "Contest not found",404
    rank=compute_standings(c)
    frozen=c.get("freeze_min",0)>0
    return render_template("standings.html", contest=c, ranking=rank, frozen=frozen)

@bp.route("/contest/<cid>/finalize", methods=["POST"])
def contest_finalize(cid):
    if "user" not in session or not session["user"].get("is_admin"): abort(403)
    c=get_contest(cid)
    if not c: return "Contest not found",404
    r=compute_standings(c)
    from models import get_users, save_users, get_ratings_log, save_ratings_log
    users=get_users(); idx={u["username"]:u for u in users}
    parts=[idx[row["username"]] for row in r if row["username"] in idx]
    if parts:
        K=120; n=len(parts); cur={p["username"]:p.get("rating",1500) for p in parts}; score={}
        for i,row in enumerate(r):
            if row["username"] not in cur: continue
            S=(n - i - 1)/(n-1) if n>1 else 1.0
            E=0.0
            for v in r:
                if v["username"]==row["username"]: continue
                Ru=cur[row["username"]]; Rv=cur[v["username"]]
                E+=1/(1+10**((Rv-Ru)/400))
            E/= (n-1) if n>1 else 1
            score[row["username"]]=cur[row["username"]]+K*(S-E)
        for u in parts:
            u["rating"]=int(round(score.get(u["username"],u.get("rating",1500))))
            u["contests"]=u.get("contests",0)+1
        save_users(users)
        logs=get_ratings_log()
        logs.append({"contest_id":c["id"],"time":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),"results":[{"user":row["username"],"rating":int(score.get(row["username"],idx[row["username"]].get("rating",1500)))} for row in r if row["username"] in idx]})
        save_ratings_log(logs)
    return redirect(f"/contest/{cid}/standings")

@bp.route("/admin/contest/<cid>/edit", methods=["GET", "POST"])
def contest_edit(cid):
    admin_required()
    contests = get_contests()
    contest = next((c for c in contests if c["id"] == cid), None)
    if not contest:
        return "Contest not found", 404

    if request.method == "POST":
        contest["title"] = request.form.get("title", contest["title"])
        contest["start"] = request.form.get("start", contest["start"])
        contest["end"] = request.form.get("end", contest["end"])
        contest["penalty"] = int(request.form.get("penalty", contest.get("penalty", 20)))
        contest["freeze_min"] = int(request.form.get("freeze_min", contest.get("freeze_min", 0)))
        contest["is_private"] = request.form.get("is_private", "off") == "on"
        wl = request.form.get("whitelist", "")
        contest["whitelist"] = [s.strip() for s in wl.split(",") if s.strip()]
        pid_str = request.form.get("problem_ids", "")
        contest["problems"] = [s.strip() for s in pid_str.split(",") if s.strip()]
        save_contests(contests)
        return redirect(url_for("contests.contest_view", cid=cid))

    problems = get_problems()
    return render_template("contest_edit.html", contest=contest, problems=problems)