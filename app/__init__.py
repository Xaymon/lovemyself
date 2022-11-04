from flask import Flask
from flask_session import Session
import os, sys
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.urandom(12)
from app import login,home,service,manage,order_withdraw,recieve,report,user
