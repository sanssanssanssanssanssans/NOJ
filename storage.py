import os, json, hashlib, datetime

DATA_DIR = "data"
FILES = [
    "board.json","users.json","problems.json","submissions.json",
    "contests.json","clarifications.json","ratings_log.json",
    "announcements.json"
]

def sha512b(b: bytes) -> str:
    return hashlib.sha512(b).hexdigest()

def _load_signed(path: str):
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, list):
        raw = json.dumps(obj, ensure_ascii=False, sort_keys=True).encode()
        wrapped = {"data": obj, "sha512": sha512b(raw)}
        with open(path, "w", encoding="utf-8") as w:
            json.dump(wrapped, w, ensure_ascii=False, indent=2)
        return obj
    data = obj.get("data", [])
    sha = obj.get("sha512", "")
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    if sha and sha != sha512b(raw):
        raise RuntimeError(f"tampered:{path}")
    return data

def _save_signed(path: str, data):
    if isinstance(data, dict) and "data" in data and "sha512" in data:
        data = data["data"]
    raw = json.dumps(data, ensure_ascii=False, sort_keys=True).encode()
    obj = {"data": data, "sha512": sha512b(raw)}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def load_json(name: str):
    return _load_signed(os.path.join(DATA_DIR, name))

def save_json(name: str, data):
    _save_signed(os.path.join(DATA_DIR, name), data)

def now_ts():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

def migrate_all():
    os.makedirs(DATA_DIR, exist_ok=True)
    for fn in FILES:
        p = os.path.join(DATA_DIR, fn)
        if not os.path.exists(p):
            init = []
            if fn == "users.json":
                init = [{"username":"admin","password":"admin","is_admin":True,"rating":1500,"contests":0}]
            _save_signed(p, init)
        else:
            try:
                _load_signed(p)
            except Exception:
                os.replace(p, p + ".bak")
                _save_signed(p, [])
