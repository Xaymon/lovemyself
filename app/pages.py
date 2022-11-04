from flask import Flask, render_template, request, redirect, url_for, session, jsonify, json
from app import app

@app.route("/lobby")
def lobby():
    return render_template('Lobby.html')

@app.route("/obtain_1")
def obtain_1():
    return render_template('Obtain_Card1.html')

@app.route("/obtain_prepack10")
def obtain_prepack10():
    return render_template('Obtain_prepack10.html')

@app.route("/obtain35000_1")
def obtain35000_1():
    return render_template('Obtain35000_1.html')

@app.route("/obtain_Card3")
def obtain_Card3():
    return render_template('Obtain_Card3.html')

@app.route("/obtain_aespaCard1")
def obtain_aespaCard1():
    return render_template('Obtain_aespaCard1.html')

@app.route("/obtain_aespa25")
def obtain_aespa25():
    return render_template('Obtain_aespa25.html')

@app.route("/obtain_exo_590_1")
def obtain_exo_590_1():
    return render_template('Obtain_exo_590_1.html')

@app.route("/obtain_exo_590_2")
def obtain_exo_590_2():
    return render_template('Obtain_exo_590_2.html')

@app.route("/obtain_exo_590_3")
def obtain_exo_590_3():
    return render_template('Obtain_exo_590_3.html')