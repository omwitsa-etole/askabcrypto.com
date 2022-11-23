from flask import Flask, render_template, request, redirect, url_for, session
import re
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager as CM
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
import pandas as pd
import time
from IPython.display import HTML
from bs4 import BeautifulSoup 
import requests
import random
import os
import sqlite3
from datetime import date

today = date.today()

#from flask_login import current_user

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--headless')
chrome_options.add_argument("disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(CM().install()), options=chrome_options)
#driver = webdriver.Chrome(options=chrome_options)
conn = sqlite3.connect('coinmarketcap-database.sqlite3')
conn.execute('CREATE TABLE IF NOT EXISTS accounts (username VARCHAR(100)  NOT NULL, email VARCHAR(100)  NOT NULL, password VARCHAR(100)  NOT NULL, approved VARCHAR(1) NOT NULL, datetime VARCHAR(100) NOT NULL)')
conn.close()
 
app = Flask(__name__)

try:
    with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
       	cursor = con.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username OR email = ?',["omwitsa-etole@gmail.com"])
        acc = cursor.fetchone()
        if not acc:
            cursor.execute('INSERT INTO accounts (username, email, password, approved, datetime) VALUES (?, ?, ?, ?, ?)', ["omwitsa-etole@gmail.com", "omwitsa-etole@gmail.com", "lov", "0", str(today)])
except:
    con.rollback()
    msg = "error during account creation"
finally:
    con.commit()
    con.close()

conn = sqlite3.connect('askabcrypto-database.sqlite3')
conn.execute('CREATE TABLE IF NOT EXISTS admins (email VARCHAR(100)  NOT NULL, password VARCHAR(100)  NOT NULL)')
conn.close()
try:
    with sqlite3.connect("askabcrypto-database.sqlite3") as con:
        cursor = con.cursor()
        cursor.execute('SELECT * FROM admins WHERE email = ?',["omwitsa-etole@gmail.com"])
        acc = cursor.fetchone()
        if not acc:
            cursor.execute('INSERT INTO admins (email, password) VALUES (?, ?)', ["omwitsa-etole@gmail.com", "lov"])
except:
    con.rollback()
    msg = "error during account creation"
finally:
    con.commit()
    con.close()
 
 
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'geeklogin'
 
#
src = []
source = []
pair = []
s = []
p = []
pir = None
currency = None
load_file = "load.html"
res = ""
res_first = ""
new_res = ""
accounts = None
accts = None
msge = None

def manual_replace(s, char, index):
    return s[:index] + char + s[index +1:]

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/account/login')


@app.route("/admin")
def admin_home():
	global accounts
	global accts
	global msge
	accounts = None
	if session.get("adm-loggedin") == None or session.get("adm-loggedin") == "None":
        	return redirect("/admin/login")
	with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
		cursor = con.cursor()
		cursor.execute('SELECT * FROM accounts WHERE approved = ?',["0"])
		accounts = cursor.fetchall()
		cursor.execute('SELECT * FROM accounts')
		accts = cursor.fetchall()
	return render_template("admin.html", msg = msge, accounts = accounts, users = len(accts))
@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
	msg = None
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		with sqlite3.connect("askabcrypto-database.sqlite3") as conn:
			cursor = conn.cursor()
			cursor.execute('SELECT * FROM admins WHERE email = ? AND password = ?',[username, password])
			account = cursor.fetchone()
			if account:
				session['adm-loggedin'] = True
				session['username'] = account[0]
				msg = 'Logged in successfully !'
				return redirect("/admin")
			else:
				msg = 'Incorrect username / password !'
				return render_template('admin-login.html', msg = msg)
			conn.close()
	return render_template('admin-login.html', msg = msg)
@app.route("/admin/approve", methods=['GET', 'POST'])
def approve():
	global accts
	global accounts
	global msge
	if session.get("adm-loggedin") == None or session.get("adm-loggedin") == "None":
        	return redirect("/admin/login")
	global accounts
	if request.method == 'POST' and 'user' in request.form:
		username = request.form["user"]
		co =  sqlite3.connect("coinmarketcap-database.sqlite3")
		cursor = co.cursor()
		cursor.execute('SELECT * FROM accounts WHERE username OR email = ?',[username])
		account = cursor.fetchone()
		if account:
			try:
				cursor.execute('UPDATE accounts SET approved = ? WHERE username OR email = ?',["1", username])
				msge = "User approved successfully"
			except Exception as e:
				co.rollback()
				msge = "Error during action"
				pass
			finally:
				co.commit()
				co.close()
				#accounts.pop(account)
	else:
		msge = "Error during action"
	return redirect("/admin")
@app.route("/admin/all_users")
def get_users():
	global accts
	global accounts
	with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
		cursor = con.cursor()
		cursor.execute('SELECT * FROM accounts')
		accts = cursor.fetchall()
		#con.close()
	return render_template("all_users.html", accounts = accts)

@app.route("/admin/signup", methods = ['GET', 'POST'])
def create_user():
	global accts
	global accounts
	global msge
	if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
		username = request.form["username"]
		email = request.form["email"]
		password = request.form["password"]
		try:
			with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
				cursor = con.cursor()
				cursor.execute('SELECT * FROM accounts WHERE username or email = ?',[email])
				acc = cursor.fetchone()
				if not acc:
					cursor.execute('INSERT INTO accounts (username, email, password, approved, datetime) VALUES (?, ?, ?, ?, ?)', [username, email, password, "0", str(today)])
					msge = "Account created successfully"
				else:
					msge = "User account already exists"
		except Exception as e:
			print(str(e))
			con.rollback()
			msge = "error during account creation"
		finally:
			con.commit()
			con.close()
	else:
		msge = "Provide all field details"
	return redirect("/admin")
@app.route("/admin/remove", methods = ['GET', 'POST'])
def remove_user():
	global msge
	if request.method == 'POST' and 'user' in request.form:
		email = request.form["user"]
		try:
			with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
				cursor = con.cursor()
				cursor.execute('SELECT * FROM accounts WHERE username or email = ?',[email])
				acc = cursor.fetchone()
				if acc:
					cursor.execute('DELETE FROM accounts WHERE username or email = ?',[email])
					msge = "Account deleted successfully"
				else:
					msge = "Error exists during transaction"
		except Exception as e:
			print(str(e))
			con.rollback()
			msge = "error during account creation"
		finally:
			con.commit()
			con.close()
	return redirect("/admin")

