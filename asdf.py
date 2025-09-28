#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys

def run(cmd, cwd=None):
    print(f"$ {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()

def main():
    repo = os.environ.get("BACKUP_REPO")
    token = os.environ.get("GH_TOKEN")
    email = os.environ.get("GIT_USER_EMAIL", "backup@example.com")
    name = os.environ.get("GIT_USER_NAME", "NOJ Backup Bot")

    if not repo or not token:
        print("❌ BACKUP_REPO or GH_TOKEN not set in environment")
        sys.exit(1)

    backup_dir = "backup_repo"
    remote_url = f"https://x-access-token:{token}@github.com/{repo}.git"
    if not os.path.exists(backup_dir):
        run(f"git clone {remote_url} {backup_dir}")
    else:
        run("git pull origin main", cwd=backup_dir)
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("⚠️ data directory not found, skipping copy")
    else:
        run(f"cp -r {data_dir}/* {backup_dir}/")
    run(f'git config user.email "{email}"', cwd=backup_dir)
    run(f'git config user.name "{name}"', cwd=backup_dir)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run("git add .", cwd=backup_dir)
    run(f'git commit -m "Backup at {ts}" || echo "Nothing to commit"', cwd=backup_dir)
    run("git push origin main", cwd=backup_dir)

    print("✅ Backup completed and pushed to GitHub")

if __name__ == "__main__":
    main()
