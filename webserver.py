import sqlite3

from flask import Flask, render_template, request, redirect
app = Flask(__name__)



from dotmap import DotMap
from bs4 import BeautifulSoup


@app.route("/create_tables", methods=["GET"])
def create_tables():
	'''this funtion creates tables in our database if they do not exist'''


	connection = sqlite3.connect('user.db')
	c = connection.cursor()

	# Create table
	c.execute("""
			CREATE TABLE IF NOT EXISTS location
            (	property_id integer PRIMARY KEY AUTOINCREMENT, 
            	latitude float NOT NULL, 
            	longitude float  NOT NULL, 
            	country text NOT NULL,
            	state text NOT NULL,
            	city text NOT NULL,
            	street text ,
            	zip_code integer NOT NULL,
            	host_id integer 
            );""")

	c.execute("""
			CREATE TABLE IF NOT EXISTS owner
        	(	host_id integer PRIMARY KEY AUTOINCREMENT,
	        	hostname text NOT NULL, 
	        	phone varchar(10) NOT NULL,
	        	email_id text NOT NULL
	        );""")

	c.execute("""
		CREATE TABLE IF NOT EXISTS property
        (	property_id integer PRIMARY KEY AUTOINCREMENT,
        	property_type text NOT NULL, 
        	capacity  integer NOT NULL, 
        	minimum_stay integer NOT NULL,
        	no_bathrooms integer NOT NULL,
        	no_beds integer NOT NULL,
        	bed_type text NOT NULL,
        	room_type text NOT NULL,
        	rate float NOT NULL
        );""")

	connection.commit()
	connection.close()

	return "OK"


@app.route("/sign_up_form_owner", methods=["GET"])
def sign_up_form_owner():
	return render_template("sign_up_form_owner.html")

@app.route("/sign_up_form_guest", methods=["GET"])
def sign_up_form_guest():
	return render_template("sign_up_form_guest.html")

@app.route("/sign_up_form_owner", methods=["POST"])
def sign_up_form_owner_post():



# 1. get all id in class form-group from the html instead of writing all of them
# 2. get values of fields from form
	html_soup = BeautifulSoup(open("templates/sign_up_form_owner.html"), 'html.parser')
	body=html_soup.find('body')
	formsoup=body.find('form')
	form_group=formsoup.find('div',class_='form-group')
	d={}
	for input_entry in form_group.find_all('input',class_='form-control'):
	    name = input_entry.get('id')
	    d[name]=request.form[name]

# allow dot notation in dict above 
	d = DotMap(d)
	    # d.append(name)
	    # d[name]=name
	print(d)

	# email = request.form["email"]
	# password = request.form["password"]
	# location = request.form["location"]
	# essay = request.form["essay"]

# 3. Populate tables
	connection = sqlite3.connect('user.db')
	c = connection.cursor()

	c.execute(""" INSERT INTO location (latitude,longitude,country,state,city,street,zip_code)
		VALUES (?, ?, ?, ?,?,?,?)""", [d.latitude,d.longitude,d.country,d.state,d.city,d.street,d.zip_code])
	c.execute(""" INSERT INTO owner (hostname, phone,email_id)
		VALUES (?, ?, ?, ?)""", [d.hostname, d.phone,d.email_id])
	connection.commit()

	return render_template("sign_up_form_owner.html", **d)

@app.route("/show_all_users", methods=["GET"])
def show_all_users():
	 
	connection = sqlite3.connect('user.db')
	c = connection.cursor()

	data = []
	for db_row in c.execute(""" SELECT email, location, essay
			FROM user """):
		data_row = {}
		data_row["email"] = db_row[0]
		data_row["location"] = db_row[1]
		data_row["essay"] = db_row[2]
		data.append(data_row)

	return render_template("show_all_users.html", data=data)

@app.route("/", methods=["GET"])
def login_form():
	return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login():
	email = request.form["email"]
	password = request.form["password"]

	connection = sqlite3.connect('user.db')
	c = connection.cursor()

	c.execute("""SELECT count(*) 
		FROM user
		WHERE email = ?
		AND password = ?""", [email, password])

	# Results into (0), or (1)

	count = c.fetchone()[0]

	if count > 0:
		# if user and password is correct, go here
		return redirect("/show_all_users")
	else:
		# if user and password is not correct, go here
		return redirect("/")

if __name__ == "__main__":
    app.run()