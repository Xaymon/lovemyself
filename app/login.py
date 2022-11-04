from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
from app import app
from kt_con import *


@app.route("/")
def index():
    return redirect(url_for('loding'))

@app.route("/loding")
def loding():
    return render_template('loading.html')

@app.route('/login')
def loginform():
    return render_template('/login/login.html')

@app.route('/login_user')
def login_user():
    return render_template('/login/login_user.html')


# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if request.method == "POST":
#         user_login = request.form.get('username')
#         pass_login = request.form.get('password')
#         sql = "SELECT username FROM user_account where username=%s and password=%s"
#         cur = gobal.con.cursor()
#         data = (user_login, pass_login,)
#         cur.execute(sql, data)
#         logii = cur.fetchone()
#         if logii:
#             print(logii[0])
#             session["name"] = request.form.get("username")
#             # session["roles"] = logii[0]
#             return redirect(url_for('loding'))
#         else:
#             return redirect(url_for('login_user'))


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
