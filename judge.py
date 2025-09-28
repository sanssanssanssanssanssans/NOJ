import os, re, sys, subprocess, shutil, platform

LANG_MULT = {"cpp":1.0,"py":float(os.environ.get("PYTHON_TIME_MULT","2.0"))}
PY_EXTRA = float(os.environ.get("PYTHON_EXTRA_SEC","0.5"))

def _nat_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.findall(r"\d+|[^\d]+", s)]

def collect_io_pairs(tc_dir: str):
    ins, outs = [], []
    for root, _, files in os.walk(tc_dir):
        for fn in files:
            path = os.path.join(root, fn)
            lower = fn.lower()
            if lower.endswith(".in"): ins.append(path)
            elif lower.endswith(".out"): outs.append(path)
    def stem(p): return re.sub(r"\.(in|out)$", "", os.path.basename(p), flags=re.I)
    in_map = {stem(p): p for p in ins}
    out_map = {stem(p): p for p in outs}
    common = sorted(set(in_map) & set(out_map), key=_nat_key)
    return [(in_map[k], out_map[k]) for k in common]

def find_spj(tc_dir: str):
    for root, _, files in os.walk(tc_dir):
        for fn in files:
            if fn.lower() == "spj.py":
                return os.path.join(root, fn)
    return None

def normalize_exact(s): return s.strip("\r\n")
def normalize_ignore_ws(s): return "".join(s.split())
def normalize_token(s): return " ".join(s.split())

def compare_outputs(u,e,mode):
    if mode=="ignore_ws": return normalize_ignore_ws(u)==normalize_ignore_ws(e)
    if mode=="token": return normalize_token(u)==normalize_token(e)
    return normalize_exact(u)==normalize_exact(e)

def run_spj(spj,input_path,expected_path,output_path,tl):
    py=os.environ.get("PYTHON_CMD") or sys.executable
    try:
        r=subprocess.run([py,spj,input_path,expected_path,output_path],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=tl)
        return r.returncode==0
    except: return False

def apply_ulimits(cmd, tl, mem_mb=256):
    if os.environ.get("NOJ_NO_LIMITS") == "1":
        return cmd
    if platform.system().lower().startswith("win"):
        return cmd
    if shutil.which("prlimit"):
        return ["prlimit","--nproc=64",f"--as={mem_mb*1024*1024}",f"--cpu={int(max(1,tl)+1)}","--nofile=256","--"] + cmd
    if shutil.which("bash"):
        pre=f"ulimit -v {mem_mb*1024}; ulimit -f 1024; ulimit -n 256; exec "
        return ["bash","-lc", pre + " ".join([subprocess.list2cmdline(cmd)])]
    return cmd

def build_and_run(language, src, exe_path, ip, op, tl, mem):
    if language=="cpp":
        comp=subprocess.run(["g++",src,"-O2","-std=c++17","-o",exe_path],capture_output=True,text=True,timeout=30)
        if comp.returncode!=0:
            return ("RE", comp.stderr[-1000:], "")
        cmd=[exe_path]
    else:
        cmd=[os.environ.get("PYTHON_CMD") or sys.executable, src]
    run_cmd=apply_ulimits(cmd,tl,mem)
    try:
        with open(ip,encoding="utf-8") as fin, open(op,"w",encoding="utf-8") as fout:
            r=subprocess.run(run_cmd,stdin=fin,stdout=fout,stderr=subprocess.PIPE,timeout=tl)
        if r.returncode!=0:
            return ("RE","", r.stderr.decode(errors="ignore")[-1000:])
    except subprocess.TimeoutExpired:
        return ("RE","", "TLE")
    except Exception as e:
        return ("RE","", str(e)[-1000:])
    return ("OK","", "")

def judge_submission(language, src, tc_dir, tl_base, mem, cmp_mode, use_spj):
    pairs = collect_io_pairs(tc_dir)
    if not pairs: return ("No IO","","")
    tl = tl_base*LANG_MULT.get(language,1.0)+(PY_EXTRA if language=="py" else 0.0)
    spj_path = find_spj(tc_dir) if use_spj else None
    exe = os.path.join(os.path.dirname(src), "a.out")
    for ip, ep in pairs:
        op = os.path.join(os.path.dirname(src), "out.txt")
        st, comp_msg, run_msg = build_and_run(language, src, exe, ip, op, tl, mem)
        if st=="RE": return ("RE", comp_msg, run_msg)
        with open(op,encoding="utf-8") as f: uo=f.read()
        with open(ep,encoding="utf-8") as f: eo=f.read()
        if spj_path and os.path.exists(spj_path):
            if not run_spj(spj_path, ip, ep, op, tl): return ("WA","","")
        else:
            if not compare_outputs(uo, eo, cmp_mode): return ("WA","","")
    return ("AC","","")
