import os
from flask import Flask, render_template, request, redirect, url_for, session
from app import app

picFolder = os.path.join('static','card')
app.config['UPLOAD_FOLDER'] = picFolder

@app.route('/home')
def home():
    # pic1 = os.path.join(app.config['UPLOAD_FOLDER'], 'SAKURA.png')
    return render_template('Shop.html')
