import sqlite3
from flask import Flask, render_template, request, redirect, flash, url_for

app = Flask(__name__)
app.secret_key = 'this_is_secret'
from dotmap import DotMap
from bs4 import BeautifulSoup


# import pdb; pdb.set_trace()


@app.route("/", methods=["GET"])
def create_tables():
    '''this funtion creates tables in our database if they do not exist'''

    connection = sqlite3.connect('user_new.db')
    c = connection.cursor()

    # Create table
    c.execute("""
            CREATE TABLE IF NOT EXISTS location
            (	property_id integer PRIMARY KEY AUTOINCREMENT, 
                country text NOT NULL,
                state text NOT NULL,
                city text NOT NULL,
                street text ,
                zip_code text
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
            no_bedrooms integer NOT NULL,
            bed_type text NOT NULL,
            room_type text NOT NULL,
            rate float NOT NULL,
            host_id integer NOT NULL
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


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    email = request.form.get("email")
    password = request.form.get("password")
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    user_type = request.form.get("user_type")
    phone = request.form.get("phone")

    connection = sqlite3.connect('user_new.db')
    c1 = connection.cursor()
    c1.execute(""" SELECT * FROM {} WHERE email=? """.format(user_type), (email,))
    user = c1.fetchall()
    connection.commit()
    print(user)
    if len(user) != 0:
        return render_template("sign_up.html", message="this email id has already  signed up!")  # **d)

    # pdb.set_trace()
    print(firstname, lastname, phone, email)
    # 3. Populate tables
    connection = sqlite3.connect('user_new.db')
    c = connection.cursor()
    if user_type == 'owner':
        c.execute(""" INSERT INTO owner (firstname,lastname, phone,email,password)
        VALUES (?, ?,? ,?,?)""", [firstname, lastname, phone, email, password])
        # GET host_id based on hostname from owner table
    elif user_type == "guest":
        c.execute(""" INSERT INTO guest (firstname,lastname, phone,email,password)
        VALUES (?, ?,? ,?,?)""", [firstname, lastname, phone, email, password])

    connection.commit()
    # G

    message = ('Welcome! You have successfully created your ' + user_type.upper() + ' account! ')
    # return redirect(url_for('login_form'),message=message)
    return render_template("sign_up.html", message=message)  # **d)


@app.route("/list_property", methods=["GET"])
def list_property_render():
    return render_template("list_property.html")


@app.route("/list_property", methods=["POST"])
def list_property():
    # 1. get all id in class form-group from the html instead of writing all of them
    # 2. get values of fields from form
   
    # check login

    email = request.form["email"]
    password = request.form["password"]

    # check email id  owner list
    connection = sqlite3.connect('user_new.db')
    c1 = connection.cursor()
    c1.execute(""" SELECT * FROM owner WHERE email=? """, (email,))
    user = c1.fetchall()
    connection.commit()

    if len(user) == 0:
        print('email not matched')
        return render_template("list_property.html", message="You email does not exist. Create an owner account to list property.")  # **d)
    elif user[0][5]!=password:
        print('password not matched')
        return render_template("list_property.html", message="You password does not match.")
    
    host_id = user[0][0]

    d = {}
    # had issues reading select class so read them in hard code
    d["street"] = request.form["street"]
    d["zip_code"] = request.form["zip_code"]
    d["rate"] = request.form["rate"]
    d["no_bathrooms"] = request.form["no_bathrooms"]
    d["no_bedrooms"] = request.form["no_bedrooms"]
    d["minimum_stay"] = request.form["minimum_stay"]
    d["capacity"] = request.form["capacity"]
    # d["rate"]=float(d["rate"])
    d["property_type"] = request.form["property_type"]
    d["bed_type"] = request.form["bed_type"]
    d["room_type"] = request.form["room_type"]
    d["country"] = request.form["country"]
    d["state"] = request.form["state"]
    d["city"] = request.form["city"]
    # allow dot notation in dict above
    d = DotMap(d)
 
    # 3. Populate tables
    connection = sqlite3.connect('user_new.db')
    c = connection.cursor()

    c.execute(""" INSERT INTO location (country,state,city,street,zipcode)
        VALUES (?, ?, ?, ?,?)""", [d.country, d.state, d.city, d.street, d.zip_code])
    # c.execute("""SET @last_id = LAST_INSERT_ID()""")
    property_id = c.lastrowid
    # print(type(property_id))
    c.execute(""" INSERT INTO property (property_id,property_type,rate,room_type,bed_type,no_bathrooms,no_bedrooms,minimum_stay,capacity, host_id)
    VALUES (?, ?, ?, ?,?,?,?,?,?,?)""",
              [property_id, d.property_type, d.rate, d.room_type, d.bed_type, d.no_bathrooms, d.no_bedrooms,
               d.minimum_stay, d.capacity, int(host_id)])

    connection.commit()

    message = (user[0][1].upper() + ' you have successfully listed a property!' + '\n' + 'Get ready to handle money and guests :) ')
    # return redirect(url_for('login_form'),message=message)
    return render_template("list_property.html", message=message)  # **d)


@app.route("/search_property", methods=["GET"])
def search_property_render():
    return render_template("search_property.html")


@app.route("/search_property", methods=["GET", "POST"])
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
    print(state, city, street, property_type, room_type, bed_type, no_bedrooms, no_bathrooms, minimum_stay, capacity,
          rate)
   
    


    sql_query_string="SELECT property.property_id, property_type, room_type, bed_type, no_bathrooms,no_bedrooms, capacity, minimum_stay, rate, state, city, street, zipcode\
    FROM property join location \
    on property.property_id = location.property_id \
    WHERE property.property_id IN \
    (SELECT property_id FROM location WHERE state= ? and city= ? and street LIKE ?)\
    and no_bathrooms>=? and no_bedrooms>=? and capacity>=? \
    and minimum_stay<=? and cast(substr(rate,2) as FLOAT)<= ? \
    and property_type=? and room_type=? and bed_type=? LIMIT 10"


# LIST OF ALL FIELDS FROM SEARCH FORM
    form_fields=[state, city, '%' + street + '%', int(no_bathrooms), int(no_bedrooms), int(capacity), int(minimum_stay),
                   float(rate)]
    optional_fields=[property_type,room_type, bed_type]

    print(">>",form_fields)
    print(">>",optional_fields)

# LIST OF VALUES THAT CAN CHANGE
    listt=['property_type','room_type','bed_type']
    to_remove=[]

    for i,value in enumerate(optional_fields):
        variable_name=listt[i]
        if value=="Any":
            print(variable_name)
            replace_string="and "+variable_name+"=?"
            print(replace_string)
            sql_query_string=sql_query_string.replace(replace_string,"")
        else:
            form_fields.append(value)
            # to_remove.append(-i)
    if street=="":

        replace_string="and street LIKE ?"
        print(replace_string)
        sql_query_string=sql_query_string.replace(replace_string,"")
        form_fields.pop(2)




    # print("check form_fields updated", form_fields)
    # print(sql_query_string,form_fields)

    connection = sqlite3.connect('user_new.db')
    c = connection.cursor()
    c.execute(sql_query_string,form_fields)
    rows = c.fetchall()
    connection.commit()


    if request.form['submit'] == 'search' and len(rows)>0:
        return render_template("search_property.html", columns=rows)

    elif request.form['submit'] == 'search' and len(rows)==0:
         return render_template("search_property.html", message="No property matches your selection.")
    
    elif request.form['submit'] == 'book':
        property_id = request.form.get('select_property')
        # print(property_id)
        # print(type(property_id))

        email = request.form["email"]
        password = request.form["password"]

        # check email id  guest list
        connection = sqlite3.connect('user_new.db')
        c1 = connection.cursor()
        c1.execute(""" SELECT * FROM guest WHERE email=? """, (email,))
        user = c1.fetchall()
        connection.commit()

        print(123)
        print(user)

        if len(user) == 0:
            print('email not matched')
            return render_template("search_property.html", message="You email does not exist. Create a guest account to book rooms.")  # **d)
        elif user[0][5]!=password:
            print('password not matched')
            return render_template("search_property.html", message="You password does not match.")
        else:
            guest_id = user[0][0]
            print(guest_id)
            booked = int(1)
            print('matched , can book')
            connection = sqlite3.connect('user_new.db')
            c2 = connection.cursor()
            c2.execute(""" INSERT INTO reservation (guest_id,property_id, booked)
                VALUES (?, ?,? )""", [int(guest_id), int(property_id),booked])
            connection.commit()
            return render_template("search_property.html", message='You have booked successfully!')
            



if __name__ == "__main__":
    app.run()

