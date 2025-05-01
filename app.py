from flask import Flask, request, session, redirect, url_for, render_template, jsonify
import os, json, uuid, zipfile, subprocess, shutil, time

app = Flask(__name__)
app.secret_key = 'supersecretkey'

os.makedirs("data", exist_ok=True)
os.makedirs("submissions", exist_ok=True)
os.makedirs("testcases", exist_ok=True)

for file in ["users.json", "problems.json", "submissions.json"]:
    path = f"data/{file}"
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([] if file != "users.json" else [{"username": "admin", "password": "admin", "is_admin": True}], f)

def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    problems = load_json("data/problems.json")
    return render_template("index.html", problems=problems, user=session.get("user"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = load_json("data/users.json")
        for u in users:
            if u['username'] == request.form['username'] and u['password'] == request.form['password']:
                session['user'] = u
                return redirect('/')
        return "Login Failed"
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = load_json("data/users.json")
        new_user = {
            "username": request.form['username'],
            "password": request.form['password'],
            "is_admin": False
        }
        users.append(new_user)
        save_json("data/users.json", users)
        return redirect('/login')
    return render_template("register.html")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user' not in session or not session['user'].get('is_admin'):
        return "Unauthorized"

    if request.method == 'POST':
        problems = load_json("data/problems.json")
        pid = str(uuid.uuid4())[:8]
        zip_file = request.files['zipfile']
        zip_path = f"testcases/{pid}.zip"
        zip_file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            extract_path = f"testcases/{pid}"
            os.makedirs(extract_path, exist_ok=True)
            zip_ref.extractall(extract_path)
        problems.append({
            "id": pid,
            "title": request.form['title'],
            "description": request.form['description'],
            "time_limit": request.form['time_limit'],
            "memory_limit": request.form['memory_limit']
        })
        save_json("data/problems.json", problems)
        return redirect('/')

    return render_template("admin.html")

@app.route('/status')
def status():
    submissions = load_json("data/submissions.json")
    return render_template("status.html", submissions=submissions)

@app.route('/problem/<pid>')
def problem(pid):
    problems = load_json("data/problems.json")
    p = next(p for p in problems if p['id'] == pid)
    return render_template("problem.html", p=p)

@app.route('/submit/<pid>', methods=['POST'])
def submit(pid):
    if 'user' not in session:
        return "Login required"

    language = request.form['language']
    code_file = request.files['code']
    sub_id = str(uuid.uuid4())[:8]
    sub_path = f"submissions/{sub_id}"
    os.makedirs(sub_path, exist_ok=True)
    ext = 'cpp' if language == 'cpp' else 'py'
    src_path = f"{sub_path}/Main.{ext}"
    code_file.save(src_path)

    testcase_dir = f"testcases/{pid}"
    inputs = sorted(f for f in os.listdir(testcase_dir) if f.endswith('.in'))
    outputs = sorted(f for f in os.listdir(testcase_dir) if f.endswith('.out'))

    verdict = 'AC'
    for i, (inp, out) in enumerate(zip(inputs, outputs)):
        input_path = os.path.join(testcase_dir, inp)
        expected_path = os.path.join(testcase_dir, out)
        with open(expected_path, encoding='utf-8') as f:
            expected = f.read().strip()

        output_path = f"{sub_path}/output.txt"
        try:
            if language == 'cpp':
                exe = f"{sub_path}/a.out"
                subprocess.run(['g++', src_path, '-o', exe], check=True)
                with open(input_path, encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8') as fout:
                    subprocess.run([exe], stdin=fin, stdout=fout, timeout=2)
            else:
                with open(input_path, encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8') as fout:
                    subprocess.run(['python3', src_path], stdin=fin, stdout=fout, timeout=2)
        except Exception as e:
            verdict = 'RE'
            break

        with open(output_path, encoding='utf-8') as f:
            user_output = f.read().strip()
        if user_output != expected:
            verdict = 'WA'
            break

    submissions = load_json("data/submissions.json")
    submissions.append({
        "username": session['user']['username'],
        "problem_id": pid,
        "result": verdict,
        "language": language,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    })
    save_json("data/submissions.json", submissions)

    shutil.rmtree(sub_path)
    return redirect('/status')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)

