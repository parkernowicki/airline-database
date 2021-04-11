
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
	query = 'SELECT * FROM flight WHERE depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME())'
	cursor.execute(query)
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('viewflights.html', flights=data)

## Jin Zhou
#Define route for viewing flights
@app.route('/newviewflights')
def newviewflights():
	return render_template('newviewflights.html')

#Search flights by source
@app.route('/flightSearch',methods=['GET','POST'])
def flightSearch():
	s_airport = request.form['sourceairport']
	d_airport = request.form['destairport']
	date = request.form['departdate']
	source = []
	if s_airport == '':
		depart = ''
	else:
		source.append(s_airport)
		depart = 'depart_airport = %s AND'
	if d_airport == '':
		arrive = ''
	else:
		source.append[d_airport]
		arrive = 'arrive_airport = %s AND'
	if date == '':
		time = ''
	else:
		source.append[date]
		time = 'depart_date = %s AND'
	query = 'SELECT * FROM flight WHERE '+depart + arrive + time + '(depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))'
	cursor = conn.cursor()
	if len(source) == 0:
		cursor.execute(query)
	else:
		cursor.execute(query,tuple(source))
	data = cursor.fetchall()
	cursor.close()
	return render_template('newviewflights.html', flights=data)

#Search flights by source
@app.route('/flightBySource', methods=['GET', 'POST'])
def flightBySource():
	#grabs information from the forms
	airport = request.form['sourceairport']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE depart_airport = %s AND (depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))'
	cursor.execute(query, (airport))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Search flights by destination
@app.route('/flightByDest', methods=['GET', 'POST'])
def flightByDest():
	airport = request.form['destairport']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE arrive_airport = %s AND (depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))'
	cursor.execute(query, (airport))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

#Search flights by date
@app.route('/flightByDate', methods=['GET', 'POST'])
def flightByDate():
	date = request.form['departdate']

	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE depart_date = %s AND (depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))'
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
	query = 'SELECT * FROM customer WHERE email = %s and password = MD5(%s)'
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
	agentid = request.form['agentID']

	cursor = conn.cursor()
	query = 'SELECT * FROM bookingagent WHERE email = %s and password = MD5(%s) and booking_agent_ID = %s'
	cursor.execute(query, (email, password, agentid))
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
	query = 'SELECT * FROM airlinestaff WHERE username = %s and user_password = MD5(%s)'
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
    userdata = cursor.fetchone()
    query = """
			SELECT
				flight.airline_name, flight.flight_num, flight.depart_date, flight.depart_time, flight.arrive_date, flight.arrive_time,
				flight.flight_status, flight.base_price, flight.depart_airport, flight.arrive_airport, flight.airplane_ID
			FROM
				customer, cust_purchases, ticket NATURAL JOIN flight
			WHERE
				customer.email = %s AND customer.email = cust_purchases.cust_email AND cust_purchases.ticket_ID = ticket.ID AND
				(flight.depart_date > CURRENT_DATE() OR (flight.depart_date = CURRENT_DATE() AND flight.depart_time > CURRENT_TIME()))
			"""
    cursor.execute(query, (email))
    flightdata = cursor.fetchall()
    cursor.close()
    return render_template('homecust.html', customer=userdata, flights=flightdata)

#Customer can purchase a ticket
@app.route('/purchaseTicketCust')
def purchaseTicketCust():
	
    cursor = conn.cursor()
    query = 'SELECT * FROM flight WHERE depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME())'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('purchaseTicketCust.html', flights=data)

#Authenticates customer ticket purchase, doesnt work quite yet...
@app.route('/purchaseTicketCustAuth', methods=['GET', 'POST'])
def purchaseTicketCustAuth():

	airline = request.form['airline']
	flightno = request.form['flightno']
	departdate = request.form['departdate']
	departtime = request.form['departtime']
	cardno = request.form['cardno']
	cardtype = request.form['cardtype']
	cardexp = request.form['cardexp']
	ticketid = request.form['ticketid']

	cursor = conn.cursor()
	query = 'SELECT * FROM ticket WHERE ID = %s'
	cursor.execute(query, (ticketid))
	ticketexists = cursor.fetchone()

	query = """
				SELECT *
				FROM
					flight
					NATURAL JOIN(
					SELECT
						airline_name, depart_date, depart_time, flight_num, COUNT(ID) AS ticketCount
					FROM
						ticket
					GROUP BY
						airline_name, depart_date, depart_time, flight_num
					) AS ticketsPerFlight,
					airplane
				WHERE
					flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s AND
					flight.airline_name = airplane.airline_name AND flight.airplane_ID = airplane.airplane_ID AND airplane.seat_amount = ticketsPerFlight.ticketCount
			"""
	cursor.execute(query, (airline, flightno, departdate, departtime))
	seatsfull = cursor.fetchone()

	query = 'SELECT name FROM customer WHERE email = %s'
	cursor.execute(query, (session['email']))
	name = cursor.fetchone()

	query = 'SELECT name FROM customer WHERE email = %s'
	cursor.execute(query, (session['email']))
	name = cursor.fetchone()

	error = None
	if(ticketexists):
		error = "Existing ticket; try another ID"
		cursor.close()
		return render_template('purchaseTicketCust.html', error=error)
	elif(seatsfull):
		error = "Seats are filled for that flight"
		cursor.close()
		return render_template('purchaseTicketCust.html', error=error)
	else:
		soldprice = 40.00 #fixing this later
		ins = 'INSERT INTO ticket VALUES(%s, 40.00, %s, %s, %s, %s, CURRENT_DATE(), CURRENT_TIME(), %s, %s, %s, %s)'
		cursor.execute(ins, (ticketid, cardno, cardtype, cardexp, name, airline, flightno, departdate, departtime))
		conn.commit()
		cursor.close()
		return redirect(url_for('homecust'))

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
	name = request.form['name']
	password = request.form['password']
	buildingno = request.form['buildingno']
	street = request.form['street']
	city = request.form['city']
	state = request.form['state']
	phonenumber = request.form['phonenumber']
	passportno = request.form['passportno']
	passportexp = request.form['passportexp']
	passportcountry = request.form['passportcountry']
	dateofbirth = request.form['dateofbirth']

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
		ins = 'INSERT INTO customer VALUES(%s, %s, MD5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (email, name, password, buildingno, street, city, state,
								phonenumber, passportno, passportexp, passportcountry, dateofbirth))
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
		ins = 'INSERT INTO bookingagent VALUES(%s, MD5(%s), %s, 0.00)'
		idquery = 'SELECT max(booking_agent_ID) FROM bookingagent'
		cursor.execute(idquery)
		id = cursor.fetchone()
		id = str(int(id['max(booking_agent_ID)']) + 1)
		cursor.execute(ins, (email, password, id.zfill(5)))
		conn.commit()
		cursor.close()
		session['email'] = email
		return redirect(url_for('homeagent'))

#Authenticates register for a new staff
@app.route('/registerStaffAuth', methods=['GET', 'POST'])
def registerStaffAuth():
	username = request.form['username']
	password = request.form['password']
	firstname = request.form['firstname']
	lastname = request.form['lastname']
	dateofbirth = request.form['dateofbirth']
	airline = request.form['airline']

	cursor = conn.cursor()
	query = 'SELECT * FROM airlinestaff WHERE username = %s'
	cursor.execute(query, (username))
	data = cursor.fetchone()
	error = None
	if(data):
		error = "Existing staff; try another username"
		return render_template('registerstaff.html', error=error)
	else:
		ins = 'INSERT INTO airlinestaff VALUES(%s, MD5(%s), %s, %s, %s, %s)'
		cursor.execute(ins, (username, password, firstname, lastname, dateofbirth, airline))
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
