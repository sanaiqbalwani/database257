import sqlite3

from flask import Flask, render_template, request, redirect,flash,url_for


app = Flask(__name__)
app.secret_key = 'this_is_secret'


from dotmap import DotMap
from bs4 import BeautifulSoup


@app.route("/", methods=["GET"])
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
	        	firstname text NOT NULL, 
	        	lastname text NOT NULL,
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

	return render_template("home.html")

	# return "OK"

@app.route("/home", methods=["GET"])
def render_home():
	return render_template("home.html")

@app.route("/sign_up", methods=["GET"])
def sign_up_render():
	return render_template("sign_up.html")


@app.route("/sign_up", methods=["POST"])
def sign_up():



# 1. get all id in class form-group from the html instead of writing all of them
# 2. get values of fields from form
	html_soup = BeautifulSoup(open("templates/sign_up.html"), 'html.parser')
	body=html_soup.find('body')
	formsoup=body.find('form')
	form_group=formsoup.find('div',class_='form-group')
	d={}
	for input_entry in form_group.find_all('input',class_='form-control'):
	    name = input_entry.get('id')
	    d[name]=request.form[name]


# allow dot notation in dict above 
	d = DotMap(d)
# 3. Populate tables
	connection = sqlite3.connect('user.db')
	c = connection.cursor()
	if d.user_type=='owner':
		c.execute(""" INSERT INTO owner (firstname,lastname, phone,email_id)
			VALUES (?, ?,? ,?)""", [d.firstname, d.lastname,d.phone,d.email_id])
		# GET host_id based on hostname from owner table 
		
		connection.commit()
	elif d.user_type=="guest": 
		c.execute(""" INSERT INTO guest (firstname,lastname, phone,email_id)
		VALUES (?, ?,? ,?)""", [d.firstname, d.lastname,d.phone,d.email_id])
		# G

	message=('Welcome! You have successfully created your account! ')
	# return redirect(url_for('login_form'),message=message)
	return render_template("sign_up.html",message=message) #**d)

@app.route("/list_property", methods=["GET"])
def list_property_render():
	return render_template("list_property.html")


@app.route("/list_property", methods=["POST"])
def list_property():
# 1. get all id in class form-group from the html instead of writing all of them
# 2. get values of fields from form
	html_soup = BeautifulSoup(open("templates/list_property.html"), 'html.parser')
	body=html_soup.find('body')
	formsoup=body.find('form')
	form_group=formsoup.find('div',class_='form-group')
	d={}
	for input_entry in form_group.find_all('input',class_='form-control'):
	    name = input_entry.get('id')
	    d[name]=request.form[name]


# allow dot notation in dict above 
	d = DotMap(d)

# 3. Populate tables
	connection = sqlite3.connect('user.db')
	c = connection.cursor()
	# GET host_id based on hostname from owner table 
	host_id=int(1111111) #filler
	# host_id=c.execute("""SELECT host_id FROM owner WHERE firstname=? AND lastname=?""",(d.firstname,d.lastname))
	# host_id=host_id.fetchone()[0]
	c.execute(""" INSERT INTO location (latitude,longitude,country,state,city,street,zip_code,host_id)
		VALUES (?, ?, ?, ?,?,?,?,?)""", [d.latitude,d.longitude,d.country,d.state,d.city,d.street,d.zip_code,host_id])
	
	connection.commit()

	message=('You have successfully listed a property! Get ready to handle money and guests :) ')
	# return redirect(url_for('login_form'),message=message)
	return render_template("list_property.html",message=message) #**d)


@app.route("/log_in", methods=["GET"])
def log_in_render():
	message=None
	return render_template("log_in.html",message=message)


@app.route("/log_in", methods=["POST"])
def log_in():

	email = request.form["email"]
	password = request.form["password"]
	user_type=request.form["user_type"]

	connection = sqlite3.connect('user.db')
	c = connection.cursor()

	if user_type=='owner':

		c.execute("""SELECT count(*) 
			FROM owner
			WHERE email = ?
			AND password = ?""", [email, password])

	elif user_type=='guest':

		c.execute("""SELECT count(*) 
			FROM guest
			WHERE email = ?
			AND password = ?""", [email, password])


	# Results into (0), or (1)

	count = c.fetchone()[0]
	#####
		#add code for serach here
	######

	if count > 0:
		# if user and password is correct, go here
		return redirect("/show_all_users")
	else:
		# if user and password is not correct, go here
		return redirect("results.html")



@app.route("/search_property", methods=["GET"])
def search_property():

	return render_template("search_property.html")


@app.route("/results", methods=["GET","POST"])
def results():


	#####
		#add code for serach here
	######
	 
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

	return render_template("results.html", data=data)

if __name__ == "__main__":
    app.run()