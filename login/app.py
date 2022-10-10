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
#from flask_login import current_user

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument('--headless')
chrome_options.add_argument("disable-dev-shm-usage")
#chrome_options.binary_location = "/app/.apt/usr/bin/google-chrome-stable"
driver = webdriver.Chrome(service=Service(CM().install()), options=chrome_options)
#driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("window.open('');")
conn = sqlite3.connect('coinmarketcap-database.sqlite3')
conn.execute('CREATE TABLE IF NOT EXISTS accounts (username VARCHAR(100)  NOT NULL, email VARCHAR(100)  NOT NULL, password VARCHAR(100)  NOT NULL)')
conn.close()
 
app = Flask(__name__)

try:
    with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
        cursor = con.cursor()
        cursor.execute('INSERT INTO accounts (username, email, password) VALUES (?, ?, ?)', ["omwitsa-etole@gmail.com", "omwitsa-etole@gmail.com", "lov"])
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
pir = ""
currency = ""
load_file = "load.html"

def manual_replace(s, char, index):
    return s[:index] + char + s[index +1:]

@app.route('/logout')
def logout():
	session['loggedin'] = None
	session['username'] = None
	return redirect('/account/login')
@app.route('/account/login', methods=['GET', 'POST'])
def login():
	global load_file
	load_file = "load.html"
	msg = 'msg'
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
			cursor = con.cursor()
			cursor.execute('SELECT * FROM accounts WHERE username OR email = ? AND password = ?',[username, password])
			account = cursor.fetchone()
			if account:
				session['loggedin'] = True
				session['username'] = account[1]
				session['name'] = account[0]
				msg = 'Logged in successfully !'
				return redirect("/")
			else:
				msg = 'Incorrect username / password !'
				return render_template('login.html', msg = msg)
	return render_template('login.html', msg = msg)
	
@app.route('/account/signup', methods=['GET', 'POST'])
def register():
	msg = 'msg'
	if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form and 'password2' in request.form :
		try:
			username = request.form['username']
			password = request.form['password']
			password2 = request.form['password2']
			email = request.form['email']
			with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
				cursor = con.cursor()
				cursor.execute('SELECT * FROM accounts WHERE email = ?', [email])
				account = cursor.fetchone()
				if account:
				    msg = 'Account email already exists !'
				cursor.execute('SELECT * FROM accounts WHERE username = ?',[username])
				account = cursor.fetchone()
				if account:
				    msg = 'Account username already exists !'
				if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				    msg = 'Invalid email address !'
				if not re.match(r'[A-Za-z0-9]+', username):
				    msg = 'Username must contain only characters and numbers !'
				if password != password2:
				    msg = 'Password do not match!'
				if not username or not password or not email or not password2:
				    msg = 'Please fill out the fields !'
				else:
				    cursor.execute('INSERT INTO accounts (username, email, password) VALUES (?, ?, ?)', [username, email, password])
				    msg = 'Account created successfully'
		except:
			con.rollback()
			msg = "error during account creation"
		finally:
			con.commit()
			con.close()
			
	return render_template('register.html', msg = msg)
@app.route('/fetching')
def fetcher():
	return render_template("loading.html")

@app.route('/t',methods =['GET', 'POST'])
def table_load():
	global p
	global s
	global src
	global pr
	global currency;global pir
	p1 = []
	p2 = [];
	for i in range(0, len(s)-1):
		p1.append(float(p[i]))
	for i in range(0, len(src)-1):
		p2.append(float(pr[i]))
	return render_template("tableload.html",m = len(src), n = len(p), p = p, s = s, pir=pir, p1 = p1, p2 = p2, source = src)

@app.route('/f', methods =['GET', 'POST'])
def loader():
	global load_file
	msg = ""
	if load_file == "load.html":
		with open(r"login/templates/load.html", 'r') as fp:
			lines = len(fp.readlines())
	else:
		with open(r"login/templates/loadpair.html", 'r') as fp:
			lines = len(fp.readlines())
	count = int(lines)
	if count + 1 < 2:
		load_file = "error404.html"
		msg = "Data could not be loaded"
	if request.method=="POST" or request.method =="GET":
		return render_template(load_file, currency = currency, msg = msg)
	return render_template(load_file, currency = currency, msg = msg)

@app.route('/other', methods =['GET', 'POST'])
def other():
    cap = None
    if request.method == 'POST' and "cap" in request.form:
        cap = reques.form["cap"]
    driver.get("https://coinmarketcap.com")
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 2000)")
    table = driver.find_element("xpath", "//div[@class='h7vnx2-1 bFzXgL']")
    soup = table.get_attribute('innerHTML') 
    ft = open("login/templates/file2.html", "w")
    ft.write(str(soup))
    ft.close()
    try:
        os.remove("login/templates/loadcap.html")
    except:
        pass
    fnd = []
    cont = 0
    with open('login/templates/file2.html', 'r') as f:
        contents = f.read();
        sup = BeautifulSoup(contents, 'html.parser');
        li = sup.findAll("td")
        lt = sup.findAll("tr")
        for l in li:
            k = l.previous_sibling
            if "$" in str(l.text):
                if "Buy" not in str(k.text):
                    g = str(l.text)
                    g = manual_replace(g, '', 0);
                    if cap is not None:
                        if int(g) <= cap and str(l.text) not in fnd:
                            fnd.append(str(l.text))
                    else:
                        fnd.append("$")   
        ft = open("login/templates/loadcap.html", "a+")
        ft.write("<table><tbody>") 
        ft.write(str(sup.tr))        
        for t in lt:
            cont += 1
            for i in fnd:
                if i in str(t.text):
                    ft.write(str(t))
                    break
        ft.write("</tbody></table>")
        ft.close()
    return render_template("other.html")
@app.route('/cap')
def cap():
    return render_template("loadcap.html")
@app.route('/dashboard')
def re_home():
	global source
	global pair
	global load_file
	global p
	global s
	global currency
	global pir
	return render_template('index.html', currency = session['currency'], urls = source, n = len(s), m = len(p), pairs = pair, pir=pir, p = p, s = s)
@app.route('/filter')
@app.route('/', methods =['GET', 'POST'])
def home():
	if session.get("loggedin") == None or session.get("loggedin") == "None":
		return redirect("/account/login")
	global source
	global pair
	global load_file
	global p
	global s
	global currency
	global pir
	source = []
	driver.get("https://coinmarketcap.com")
	time.sleep(1)
	
	vx = driver.find_elements(By.TAG_NAME, "a")
	time.sleep(1)
	for v in vx:
		if "https://coinmarketcap.com/currencies/" in str(v.get_attribute('href')):
			k = str(v.get_attribute('href'))
			k = k.replace("https://coinmarketcap.com/currencies/", "")
			k = k.split('/')
			if k[0] not in source:
				source.append(k[0])
	pir = ""
	if request.method == 'POST' and "pair" in request.form:
		currency = request.form['currency']
		pir = request.form['pair']
	#load(currency)
	if currency == "":
		if session.get('currency') is not None:
			currency = session['currency']
		else:
			currency = random.choice(source)
			session['currency'] = currency
	else:
		session['currency'] = currency
	#print(currency)
	load(driver, currency, pir)
	return render_template('index.html', currency = session['currency'], urls = source, n = len(s), m = len(p), pairs = pair, pir=pir, p = p, s = s)
def load(driver, crc, pir):
	global source
	global url
	global pair
	global load_file
	global s
	global p
	global src
	global pr
	src = []
	pr = []
	count = 0
	cont = 0
	p = []
	s = []
	#pair = []
	while True:	
		if count == 1 or count > 1:
			load_file = "error404.html"
			break
		count += 1	
		url = "https://coinmarketcap.com/currencies/"+crc+"/"
		driver.get(url)	
		#driver.execute_script("window.scrollTo(0, 1700)")
		time.sleep(1)	
		vx = driver.find_elements(By.TAG_NAME, "a")
		#page_source = requests.get(url+"markets/") 
		try:
			driver.find_element("xpath", "//div[@class='']").click()
			break
		except:
			pass
		driver.get(url+"markets/")
		time.sleep(3)
		
		#driver.refresh()
		if pir == "":
			driver.execute_script("window.scrollTo(0, 1500)")
			while True:
				try:
					table = driver.find_element("xpath", '//div[@class="h7vnx2-1 kUATHk"]')
					soup = table.get_attribute('innerHTML') 
					time.sleep(2)
					break
				except:
					pass	
					
			text_file = open("login/templates/file.html", "w")
			text_file.write(soup)
			text_file.close()
			try:
				os.remove('login/templates/load.html')
			except:
				pass
			ft = open("login/templates/load.html", "a+")
			ft.write("<table>")
			with open('login/templates/file.html', 'r') as f:
				contents = f.read();pair = []

				sup = BeautifulSoup(contents, 'html.parser');ft.write(str(sup.tr))
				for child in sup.recursiveChildGenerator():
					if child.name == "tr":
						if "Recently" in child.text:
							ft.write(str(child))
						if "Loading data" in child.text:
							load_file = "error404.html"
							break
				li = sup.findAll('a')
				for l in li:
                
					if "/" in str(l.text) and str(l.text) not in pair:
						pair.append(str(l.text))
				ft.write("</table>")
				ft.close()
			load_file = "load.html"
		else:
			#try:
			os.remove('login/templates/loadpair.html')
			ft = open("login/templates/loadpair.html", "a+")
			#table = driver.find_element("xpath", "//div[@class='h7vnx2-1 kUATHk']")
			with open('login/templates/load.html', 'r') as f:
				contents = f.read();count = 0;
				sup = BeautifulSoup(contents, 'html.parser')
				li = sup.findAll('td')
				tr = sup.findAll('tr')
				for l in li:
					k = l.previous_sibling
					if pir == str(l.text):
						f = l.find_next_sibling("td");count += 1; 
						g = str(f.text)
						g = manual_replace(g, '', 0);pr.append(g);src.append(str(k.text))
						#if f is not None or f != "None":
						p.append(g)
						s.append(str(l.text))
				ft.write("<table><tbody>")
				ft.write(str(sup.tr))
				for t in tr:
					if pir in str(t.text):
						cont = 1
						ft.write(str(t))
				if(cont == 0):		
					ft.write("<center><p style='font-size: 20px;margin-top: 5%;'>No data found from pair</p></center>")
				ft.write("</tbody></table>")
				ft.close()
				load_file = "loadpair.html"
		return
		driver.close()
		break
@app.route('/settings',methods =['GET', 'POST'])
def settings():
	if session.get("loggedin") == None or session.get("loggedin") == "None":
		return redirect("/account/login")
	msg = "msg"
	if request.method == "POST":
		if "password-change" in request.form and "password-change-confirm" in request.form and "password" in request.form:
			username = session['username']
			password = request.form['password']
			password1 = request.form['password-change']
			password2 = request.form['password-change-confirm']
			if password1 == password2:
				with sqlite3.connect("coinmarketcap-database.sqlite3") as con:
					cursor = con.cursor()
					cursor.execute('SELECT * FROM accounts WHERE username OR email = ? AND password = ?',[username, password])
					account = cursor.fetchone()
					print(username)
					if account:
						try:
							cursor.execute('UPDATE accounts SET password = ? WHERE username OR email = ?',[password1, username])
							msg = "Password changed successfully"
						except Exception as e:
							print(str(e))
							pass
						finally:
							con.commit()
							con.close()
					else:
						msg = "Incorrect password"
			else:
				msg = "Passwords do not match"
		else:
			msg = "fill out all fields"
	return render_template("404.html", msg = msg)
