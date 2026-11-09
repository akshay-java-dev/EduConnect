from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,current_user
from .extensions import db,bcrypt
from .models import User
auth=Blueprint("auth",__name__)
@auth.route("/register",methods=["GET","POST"])
def register():
    if current_user.is_authenticated: return redirect(url_for("main.home"))
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower()
        password=request.form.get("password",""); confirm=request.form.get("confirm_password","")
        if not name or not email or len(password)<8: flash("Enter valid details and an 8+ character password.","danger")
        elif password!=confirm: flash("Passwords do not match.","danger")
        elif User.query.filter_by(email=email).first(): flash("Email already registered.","danger")
        else:
            u=User(name=name,email=email,role="student"); u.set_password(password,bcrypt)
            db.session.add(u); db.session.commit(); flash("Account created. Please log in.","success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")
@auth.route("/login",methods=["GET","POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("admin.dashboard" if current_user.role=="admin" else "student.dashboard"))
    if request.method=="POST":
        email=request.form.get("email","").strip().lower(); password=request.form.get("password","")
        u=User.query.filter_by(email=email).first()
        if u and u.check_password(password,bcrypt):
            login_user(u); return redirect(url_for("admin.dashboard" if u.role=="admin" else "student.dashboard"))
        flash("Invalid email or password.","danger")
    return render_template("auth/login.html")
@auth.post("/logout")
def logout():
    logout_user(); return redirect(url_for("main.home"))
