from flask import Flask, session
import os
from storage import migrate_all, DATA_DIR
from blueprints.auth import bp as auth_bp
from blueprints.main import bp as main_bp
from blueprints.problems import bp as problems_bp
from blueprints.contests import bp as contests_bp
from blueprints.submissions import bp as submissions_bp
from blueprints.board import bp as board_bp
from blueprints.ranking import bp as ranking_bp
from blueprints.clarifications import bp as clarifications_bp
from blueprints.announcements import bp as announcements_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("APP_SECRET", "supersecretkey")
    app.config.update(
        SESSION_COOKIE_NAME="noj_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=60*60*24*14,
        SESSION_REFRESH_EACH_REQUEST=True,
        PREFERRED_URL_SCHEME="http",
        SERVER_NAME=None,
    )
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs("submissions", exist_ok=True)
    os.makedirs("testcases", exist_ok=True)
    migrate_all()
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(problems_bp)
    app.register_blueprint(contests_bp)
    app.register_blueprint(submissions_bp)
    app.register_blueprint(board_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(clarifications_bp)
    app.register_blueprint(announcements_bp)
    @app.context_processor
    def inject_user():
        return {"user": session.get("user")}
    alias_map = [
        ("/problem/<pid>","problem","problems.problem"),
        ("/submit/<pid>","submit","submissions.submit"),
        ("/status","status","main.status"),
        ("/admin_panel","admin_panel","problems.admin_panel"),
        ("/admin/problem/<pid>/edit","admin_problem_edit","problems.admin_problem_edit"),
        ("/admin/problem/new","admin_problem_new","problems.admin_problem_new"),
        ("/admin","admin","problems.admin_legacy"),
        ("/problems","problems","problems.problems_list"),
        ("/contests","contests","contests.contests_list"),
        ("/contest_admin","contest_admin","contests.contest_admin"),
        ("/contest/<cid>","contest","contests.contest_view"),
        ("/contest/<cid>","contest_view","contests.contest_view"),
        ("/contest/<cid>/join","contest_join","contests.contest_join"),
        ("/contest/<cid>/standings","contest_standings","contests.contest_standings"),
        ("/contest/<cid>/finalize","contest_finalize","contests.contest_finalize"),
        ("/clarifications/<cid>","clarifications","clarifications.clarifications"),
        ("/clarifications/<cid>/answer/<qid>","clarifications_answer","clarifications.clarifications_answer"),
        ("/ranking","ranking","ranking.ranking"),
        ("/user/<username>","user","ranking.user_profile"),
        ("/user/<username>","user_profile","ranking.user_profile"),
        ("/board","board","board.board_list"),
        ("/board/new","board_new","board.board_new"),
        ("/board/<tid>","board_thread","board.board_thread"),
        ("/admin/contest/<cid>/edit", "contest_edit", "contests.contest_edit"),
        ("/login","login","auth.login"),
        ("/logout","logout","auth.logout"),
        ("/register","register","auth.register"),
        ("/announcements","announcements","announcements.list_ann"),
        ("/admin/announcement/new","announcement_new","announcements.new_ann"),
        ("/api/submission/<sid>","api_submission","submissions.api_submission"),
    ]
    for rule, alias_ep, target_ep in alias_map:
        if target_ep in app.view_functions:
            try:
                app.add_url_rule(rule, endpoint=alias_ep, view_func=app.view_functions[target_ep])
            except Exception:
                pass
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, use_reloader=False)
