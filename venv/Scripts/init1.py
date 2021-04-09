#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port = 3306,
                       user='root',
                       password='',
                       db='airline',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#Define a route for main page
@app.route('/')
def index():
	return render_template('index.html')

#Define route for viewing flights
@app.route('/viewflights')
def viewflights():
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = 'SELECT * FROM flight WHERE depart_date >= CURRENT_DATE() AND depart_date >= CURRENT_TIME()'
	cursor.execute(query)
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Search flights by source
@app.route('/flightBySource', methods=['GET', 'POST'])
def flightBySource():
	#grabs information from the forms
	airport = request.form['sourceairport']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE depart_airport = %s AND depart_date >= CURRENT_DATE() AND depart_date >= CURRENT_TIME()'
	cursor.execute(query, (airport))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Search flights by destination
@app.route('/flightByDest', methods=['GET', 'POST'])
def flightByDest():
	airport = request.form['destairport']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE arrive_airport = %s AND depart_date >= CURRENT_DATE() AND depart_date >= CURRENT_TIME()'
	cursor.execute(query, (airport))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Search flights by date
@app.route('/flightByDate', methods=['GET', 'POST'])
def flightByDate():
	date = request.form['departdate']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE depart_date = %s AND depart_date >= CURRENT_DATE() AND depart_date >= CURRENT_TIME()'
	cursor.execute(query, (date))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Define route for customer login
@app.route('/logincust')
def logincust():
	return render_template('logincust.html')

#Define route for agent login
@app.route('/loginagent')
def loginagent():
	return render_template('loginagent.html')

#Define route for staff login
@app.route('/loginstaff')
def loginstaff():
	return render_template('loginstaff.html')

#Authenticates the customer login
@app.route('/loginCustAuth', methods=['GET', 'POST'])
def loginCustAuth():
	email = request.form['email']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		#creates a session for the the customer, session is a built in
		session['email'] = email
		return redirect(url_for('homecust'))
	else:
		#returns an error message to the html page
		error = 'Invalid login or email'
		return render_template('logincust.html', error=error)

#Authenticates the agent login
@app.route('/loginAgentAuth', methods=['GET', 'POST'])
def loginAgentAuth():
	email = request.form['email']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM bookingagent WHERE email = %s and password = %s'
	cursor.execute(query, (email, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		session['email'] = email
		return redirect(url_for('homeagent'))
	else:
		error = 'Invalid login or email'
		return render_template('loginagent.html', error=error)

#Authenticates the staff login
@app.route('/loginStaffAuth', methods=['GET', 'POST'])
def loginStaffAuth():
	username = request.form['username']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM airlinestaff WHERE username = %s and user_password = %s'
	cursor.execute(query, (username, password))
	data = cursor.fetchone()
	cursor.close()
	error = None
	if(data):
		session['username'] = username
		return redirect(url_for('homestaff'))
	else:
		error = 'Invalid login or email'
		return render_template('loginstaff.html', error=error)

#Home page for customer
@app.route('/homecust')
def homecust():

    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * FROM customer WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone() 
    cursor.close()
    return render_template('homecust.html', customer=data)

#Home page for agent
@app.route('/homeagent')
def homeagent():

    email = session['email']
    cursor = conn.cursor()
    query = 'SELECT * FROM bookingagent WHERE email = %s'
    cursor.execute(query, (email))
    data = cursor.fetchone() 
    cursor.close()
    return render_template('homeagent.html', bookingagent=data)

#Home page for staff
@app.route('/homestaff')
def homestaff():

    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT * FROM airlinestaff WHERE username = %s'
    cursor.execute(query, (username))
    data = cursor.fetchone() 
    cursor.close()
    return render_template('homestaff.html', airlinestaff=data)

#Define route to register customer
@app.route('/registercust')
def registercust():
	return render_template('registercust.html')

#Define route to register agent
@app.route('/registeragent')
def registeragent():
	return render_template('registeragent.html')

#Define route to register staff
@app.route('/registerstaff')
def registerstaff():
	return render_template('registerstaff.html')

#Authenticates register for a new customer
@app.route('/registerCustAuth', methods=['GET', 'POST'])
def registerCustAuth():
	email = request.form['email']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM customer WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):
		#If the previous query returns data, then user exists
		error = "Existing customer; try another email address"
		return render_template('registercust.html', error=error)
	else:
		#Might want to require these NULL attributes to be filled out later...
		ins = 'INSERT INTO customer VALUES(%s, NULL, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)'
		cursor.execute(ins, (email, password))
		conn.commit()
		cursor.close()
		session['email'] = email
		return redirect(url_for('homecust'))

#Authenticates register for a new agent
@app.route('/registerAgentAuth', methods=['GET', 'POST'])
def registerAgentAuth():
	email = request.form['email']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM bookingagent WHERE email = %s'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "Existing agent; try another email address"
		return render_template('registeragent.html', error=error)
	else:
		ins = 'INSERT INTO bookingagent VALUES(%s, %s, NULL, NULL)'
		cursor.execute(ins, (email, password))
		conn.commit()
		cursor.close()
		session['email'] = email
		return redirect(url_for('homeagent'))

#Authenticates register for a new staff
@app.route('/registerStaffAuth', methods=['GET', 'POST'])
def registerStaffAuth():
	username = request.form['username']
	password = request.form['password']

	cursor = conn.cursor()
	query = 'SELECT * FROM airlinestaff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "Existing staff; try another username"
		return render_template('registerstaff.html', error=error)
	else:
		ins = 'INSERT INTO airlinestaff VALUES(%s, %s, NULL, NULL, NULL, NULL)'
		cursor.execute(ins, (username, password))
		conn.commit()
		cursor.close()
		session['username'] = username
		return redirect(url_for('homestaff'))

#Logout for customers and agents
@app.route('/logoutemail')
def logoutemail():
	session.pop('email')
	return redirect('/')

#Logout for staff
@app.route('/logoutusername')
def logoutusername():
	session.pop('username')
	return redirect('/')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
