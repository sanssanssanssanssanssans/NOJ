from flask import Blueprint, render_template, request, redirect, session
from models import get_users, save_users
import os

bp = Blueprint("auth", __name__)
ADMIN_USER = os.environ.get("ADMIN_USER","admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]; pw=request.form["password"]
        if u==ADMIN_USER:
            if ADMIN_PASSWORD is None: return "Admin login is not configured.",500
            if pw==ADMIN_PASSWORD:
                session["user"]={"username":u,"is_admin":True,"rating":1500}
                session.permanent = True
                return redirect("/")
            return "Login Failed",401
        users=get_users()
        for x in users:
            if x.get("username")==u and x.get("password")==pw:
                session["user"]={"username":x["username"],"is_admin":x.get("is_admin",False),"rating":x.get("rating",1500)}
                session.permanent = True
                return redirect("/")
        return "Login Failed",401
    return render_template("login.html")

@bp.route("/logout")
def logout():
    session.clear(); return redirect("/")

@bp.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        users=get_users()
        u=request.form["username"]; pw=request.form["password"]
        if any(x["username"]==u for x in users): return "Username exists",400
        users.append({"username":u,"password":pw,"is_admin":False,"rating":1500,"contests":0})
        save_users(users)
        return redirect("/login")
    return render_template("register.html")
