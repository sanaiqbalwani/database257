import sqlite3
from flask import Flask, render_template, request, redirect,flash,url_for
app = Flask(__name__)
app.secret_key = 'this_is_secret'
from dotmap import DotMap
from bs4 import BeautifulSoup

# import pdb; pdb.set_trace()


@app.route("/", methods=["GET"])
def create_tables():
    '''this funtion creates tables in our database if they do not exist'''


    connection = sqlite3.connect('user.db')
    c = connection.cursor()

    # Create table
    c.execute("""
            CREATE TABLE IF NOT EXISTS location
            (	property_id integer PRIMARY KEY AUTOINCREMENT, 
                country text NOT NULL,
                state text NOT NULL,
                city text NOT NULL,
                street text ,
                zip_code text,
                host_id integer 
            );""")

    c.execute("""
            CREATE TABLE IF NOT EXISTS owner
            (	host_id integer PRIMARY KEY AUTOINCREMENT,
                firstname text NOT NULL, 
                lastname text NOT NULL,
                phone varchar(10) NOT NULL,
                email text NOT NULL,
                password text NOT NULL
            );""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS property
        (	property_id integer PRIMARY KEY AUTOINCREMENT,
            property_type text NOT NULL, 
            capacity  integer NOT NULL, 
            minimum_stay integer NOT NULL,
            no_bathrooms float NOT NULL,
            no_beds integer NOT NULL,
            bed_type text NOT NULL,
            room_type text NOT NULL,
            rate float NOT NULL
        );""")

    c.execute("""
        CREATE TABLE IF NOT EXISTS guest
        (   guest_id integer PRIMARY KEY AUTOINCREMENT,
            firstname text NOT NULL, 
            lastname text NOT NULL,
            phone varchar(10) NOT NULL,
            email text NOT NULL,
            password text NOT NULL
        );""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS reservation
    (   property_id integer,
        guest_id integer,
        booked integer NOT NULL 
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


@app.route("/sign_up", methods=["GET","POST"])
def sign_up():
    email = request.form.get("email")
    password = request.form.get("password")
    firstname=request.form.get("firstname")
    lastname=request.form.get ("lastname")
    user_type=request.form.get("user_type")
    phone=request.form.get("phone")

    connection = sqlite3.connect('user.db')
    c1 = connection.cursor()
    c1.execute(""" SELECT * FROM {} WHERE email=? """.format(user_type),(email,))
    user= c1.fetchall()
    connection.commit()
    print(user)
    if len(user)!=0:
        return render_template("sign_up.html",message="this email id has already  signed up!") #**d)
    
    # pdb.set_trace()
    print(firstname,lastname,phone,email)
# 3. Populate tables
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    if user_type=='owner':
        c.execute(""" INSERT INTO owner (firstname,lastname, phone,email,password)
        VALUES (?, ?,? ,?,?)""", [firstname,lastname,phone,email,password])
        # GET host_id based on hostname from owner table
    elif user_type=="guest":
        c.execute(""" INSERT INTO guest (firstname,lastname, phone,email,password)
        VALUES (?, ?,? ,?,?)""", [firstname, lastname,phone,email,password])

    connection.commit()
        # G

    message=('Welcome! You have successfully created your '+ user_type.upper()+' account! ')
    # return redirect(url_for('login_form'),message=message)
    return render_template("sign_up.html",message=message) #**d)

@app.route("/list_property", methods=["GET"])
def list_property_render():
    return render_template("list_property.html")

@app.route("/list_property", methods=["POST"])
def list_property():
# 1. get all id in class form-group from the html instead of writing all of them
# 2. get values of fields from form
    user_type=request.form["user_type"]
    if user_type=="guest":
        return render_template("list_property.html",message="You should signup as an OWNER") #**d)
    # check login
    email=request.form["email"]
    password=request.form["password"]
    connection = sqlite3.connect('user.db')
    c1 = connection.cursor()
    c1.execute(""" SELECT * FROM owner WHERE email=? and password=? """,(email,password,))
    user= c1.fetchall()
    connection.commit()
    print(user)
    if len(user)==0:
        return render_template("list_property.html",message="You email/password is wrong or do not exist.") #**d)

    d={}
    # had issues reading select class so read them in hard code
    d["street"]=request.form["street"]
    d["zip_code"]=request.form["zip_code"]
    d["rate"]=request.form["rate"]
    d["no_bathrooms"]=request.form["no_bathrooms"]
    d["no_beds"]=request.form["no_beds"]
    d["minimum_stay"]=request.form["minimum_stay"]
    d["capacity"]=request.form["capacity"]
    # d["rate"]=float(d["rate"])
    d["property_type"]=request.form["property_type"]
    d["bed_type"]=request.form["bed_type"]
    d["room_type"]=request.form["room_type"]
    d["country"]=request.form["country"]
    d["state"]=request.form["state"]
    d["city"]=request.form["city"]
# allow dot notation in dict above 
    d = DotMap(d)
    print(d)
    print(user[0])
# 3. Populate tables
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    # GET host_id based on hostname from owner table
    host_id=int(1111111) #filler
    # host_id=c.execute("""SELECT host_id FROM owner WHERE firstname=? AND lastname=?""",(d.firstname,d.lastname))
    # host_id=host_id.fetchone()[0]
    c.execute(""" INSERT INTO location (country,state,city,street,zip_code,host_id)
        VALUES (?, ?, ?, ?,?,?)""", [d.country,d.state,d.city,d.street,d.zip_code,host_id])
    # c.execute("""SET @last_id = LAST_INSERT_ID()""")
    property_id=c.lastrowid
    # print(type(property_id))
    c.execute(""" INSERT INTO property (property_id,property_type,rate,room_type,bed_type,no_bathrooms,no_beds,minimum_stay,capacity)
    VALUES (?, ?, ?, ?,?,?,?,?,?)""", [property_id,d.property_type,d.rate,d.room_type,d.bed_type,d.no_bathrooms,d.no_beds,d.minimum_stay,d.capacity])

    connection.commit()
    # user[1].upper(),

    message=(user[0][1].upper()+' you have successfully listed a property!'+'\n'+'Get ready to handle money and guests :) ')
    # return redirect(url_for('login_form'),message=message)
    return render_template("list_property.html",message=message) #**d)



@app.route("/search_property", methods=["GET"])
def search_property_render():
    message=None
    return render_template("search_property.html",message=message)

@app.route("/search_property", methods=["GET","POST"])
def search_property():

    state = request.form['state']
    city = request.form['city']
    street = request.form['street']
    property_type = request.form['property_type']
    room_type = request.form['room_type']
    bed_type = request.form['bed_type']
    no_bathrooms = request.form['no_bathrooms']
    no_bedrooms = request.form['no_bedrooms']
    minimum_stay = request.form['minimum_stay']
    capacity = request.form['capacity']
    rate = request.form['rate']
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    # if street != '':
    #     # select_stmt = "SELECT * FROM employees WHERE emp_no = %(emp_no)s"
    #     # c.execute(select_stmt, {'emp_no': 2})
    #     # ---------
    #     c.execute(""" SELECT * FROM property  WHERE property_id IN
    #      (SELECT property_id FROM location WHERE state= ? and city= ?and street=?)""",[state,city,street])
     


    #     # ---------
    #     # select_stmt = """ select * from property where property_id in 
    #     #     (select property_id from location where state=%(state)s and city=%(city)s and street=%(street)s) """
    #     # c.execute(select_stmt, {'state': state, 'city': city})
    #     rows = c.fetchall()
    #     connection.commit()
    # else:
    c.execute(""" SELECT * FROM property  WHERE property_id IN
     (SELECT property_id FROM location WHERE state= ? and city= ?)""",(state,city,))

    rows = c.fetchall()
    connection.commit()
  
    print (rows,state, city, street)
    return render_template("search_property.html", colums=rows)#**locals())

if __name__ == "__main__":
    app.run()