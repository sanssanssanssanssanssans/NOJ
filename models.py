from storage import load_json, save_json
import datetime

def get_users(): return load_json("users.json")
def save_users(users): save_json("users.json", users)

def get_problems(): return load_json("problems.json")
def save_problems(problems): save_json("problems.json", problems)
def get_problem(pid):
    ps = get_problems()
    return next((p for p in ps if p["id"] == pid), None)

def get_contests(): return load_json("contests.json")
def save_contests(contests): save_json("contests.json", contests)
def get_contest(cid):
    cs = get_contests()
    return next((c for c in cs if c["id"] == cid), None)

def get_submissions(): return load_json("submissions.json")
def save_submissions(subs): save_json("submissions.json", subs)

def get_board(): return load_json("board.json")
def save_board(items): save_json("board.json", items)

def get_clarifications(): return load_json("clarifications.json")
def save_clarifications(items): save_json("clarifications.json", items)

def get_ratings_log(): return load_json("ratings_log.json")
def save_ratings_log(logs): save_json("ratings_log.json", logs)

def get_announcements(): return load_json("announcements.json")
def save_announcements(items): save_json("announcements.json", items)

def parse_ts(s):
    try: return datetime.datetime.fromisoformat(s)
    except: return None

def in_window(ts, start, end):
    t = parse_ts(ts); s = parse_ts(start); e = parse_ts(end)
    return bool(t and s and e and s <= t <= e)
