from flask import Blueprint, request, redirect, session, abort, jsonify
import os, re, uuid, shutil, datetime
from models import get_problem, get_contest, get_submissions, save_submissions
from judge import judge_submission

bp = Blueprint("submissions", __name__)

@bp.route("/submit/<pid>", methods=["POST"])
def submit(pid):
    if "user" not in session: abort(401)
    language=request.form["language"]
    code_file=request.files.get("code")
    code_text=request.form.get("code_text","")

    contest_id = (
        request.form.get("contest_id")
        or request.args.get("contest_id")
        or session.get("current_contest")
        or None
    )


    p=get_problem(pid)
    if not p: return "Problem not found",404
    if contest_id:
        c=get_contest(contest_id)
        if not c: return "Contest not found",404
        if c.get("is_private") and session["user"]["username"] not in c.get("whitelist",[]): return "No access",403

    sub_id=str(uuid.uuid4())[:8]
    sub_path=f"submissions/{sub_id}"
    os.makedirs(sub_path,exist_ok=True)
    ext="cpp" if language=="cpp" else "py"
    src=f"{sub_path}/Main.{ext}"
    if code_file and code_file.filename:
        if not re.search(r"\.(cpp|py)$",code_file.filename,flags=re.I):
            shutil.rmtree(sub_path,ignore_errors=True); return "Invalid file",400
        code_file.save(src)
    else:
        with open(src,"w",encoding="utf-8") as f: f.write(code_text)

    v=int(p.get("tc_version",1))
    tc_dir=f"testcases/{pid}/v{v}"
    if not os.path.isdir(tc_dir):
        shutil.rmtree(sub_path,ignore_errors=True); return "Testcases missing",404
    base_tl=float(p.get("time_limit",2)); mem=int(p.get("memory_limit",256))
    cmp_mode=p.get("cmp","exact") or "exact"
    verdict, compile_msg, run_msg = judge_submission(language, src, tc_dir, base_tl, mem, cmp_mode, p.get("spj",False))

    subs=get_submissions()
    subs.append({
        "id":sub_id,"username":session["user"]["username"],"problem_id":pid,
        "contest_id":contest_id,"result":verdict,"language":language,
        "timestamp":datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "compile":compile_msg,"stderr":run_msg,"tc_version":v
    })
    save_submissions(subs)
    shutil.rmtree(sub_path,ignore_errors=True)
    return redirect(f"/contest/{contest_id}/standings" if contest_id else "/status")

@bp.route("/api/submission/<sid>")
def api_submission(sid):
    subs = get_submissions()
    s = next((x for x in subs if x.get("id") == sid), None)
    if not s:
        return jsonify({"error": "not found"}), 404
    return jsonify(s)
