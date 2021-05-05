
#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect
import decimal, pymysql.cursors

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
					   port = 8889, #Make sure this matches your database port!
                       user='root',
                       password='root', #Make sure this matches too
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

#Search flights
@app.route('/flightSearch',methods=['GET','POST'])
def flightSearch():
	sourceairport = request.form['sourceairport']
	destairport = request.form['destairport']
	departdate = request.form['departdate']
	returndate = request.form['returndate']
	flightsearch = []
	if sourceairport == '':
		depart_q = ''
	else:
		flightsearch.append(sourceairport)
		depart_q = 'depart_airport = %s AND '
	if destairport == '':
		arrive_q = ''
	else:
		flightsearch.append(destairport)
		arrive_q = 'arrive_airport = %s AND '
	if departdate == '':
		ddate_q = ''
	else:
		flightsearch.append(departdate)
		ddate_q = 'depart_date = %s AND '
	cursor = conn.cursor()
	query = 'SELECT * FROM flight WHERE ' + depart_q + arrive_q + ddate_q + '(depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))'
	cursor.execute(query, tuple(flightsearch))
	data = cursor.fetchall()
	#round-trip
	if returndate != '' and sourceairport != '' and destairport != '' and departdate != '' and returndate > departdate:
		flightsearch[0] = destairport
		flightsearch[1] = sourceairport
		flightsearch[2] = returndate
		cursor.execute(query, tuple(flightsearch))
		data += cursor.fetchall()
	cursor.close()
	return render_template('viewflights.html', flights=data)

####################
#STAFF VIEW FLIGHTS
####################
#Define route for Staff viewing flights
@app.route('/viewflightsStaff')
def viewflightsStaff():
    #cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = '''
    SELECT flight.airline_name, flight_num, depart_date, depart_time, arrive_date, arrive_time,flight_status, base_price, depart_airport, arrive_airport, airplane_ID 
    FROM airlineStaff, flight 
    WHERE airlineStaff.airline_name = flight.airline_name AND DATEDIFF(depart_date,CURRENT_DATE()) <= 30 AND DATEDIFF(depart_date, CURRENT_DATE()) >= 0
    '''
    #default flight view within 30 days
	cursor.execute(query)
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('viewflightsStaff.html', flights=data)

####################
#STAFF SEARCH FLIGHTS
####################

#Search flights by source Staff
@app.route('/flightBySourceStaff', methods=['GET', 'POST'])
def flightBySourceStaff():
	#grabs information from the forms
	airport = request.form['sourceairport']
	username = session['username']
	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM flight WHERE depart_airport = %s AND airline_name = %s'
	cursor.execute(query, (airport, airline['airline_name']))
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('viewflightsStaff.html', flights=data)

#Search flights by destination
@app.route('/flightByDestStaff', methods=['GET', 'POST'])
def flightByDest():
	airport = request.form['destairport']

	username = session['username']
	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM flight WHERE arrive_airport = %s AND airline_name = %s'
	cursor.execute(query, (airport, airline['airline_name']))
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflightsStaff.html', flights=data)

#Search flights by date
@app.route('/flightByDateRange', methods=['GET', 'POST'])
def flightByDateRange():
	startdate = request.form['startdate']
	enddate = request.form['enddate']

	username = session['username']
	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM flight WHERE depart_date >= %s AND depart_date <= %s AND airline_name = %s' 
	cursor.execute(query, (startdate, enddate, airline['airline_name']))
	
	data = cursor.fetchall()
	cursor.close()
	return render_template('viewflightsStaff.html', flights=data)

#Define route for passenger list
@app.route('/passengerList/<airlinename>/<flightnum>/<depdate>/<deptime>/')
def passengerList(airlinename, flightnum, depdate, deptime):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = '''
    SELECT name, phone_number, passport_number, passport_expiration
	FROM customer, cust_purchases, ticket 
	WHERE customer.email = cust_purchases.cust_email AND cust_purchases.ticket_ID = ticket.ID
	AND airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s
	'''
    #default flight view within 30 days
	cursor.execute(query, (airlinename, flightnum, depdate, deptime))
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('passengerList.html', passenger = data)

#Define route for adding flight
@app.route('/addFlight')
def addFlight():
	#cursor used to send queries
	username = session['username']
	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	#executes query
	query = '''
    SELECT flight.airline_name, flight_num, depart_date, depart_time, arrive_date, arrive_time,flight_status, base_price, depart_airport, arrive_airport, airplane_ID 
    FROM airlineStaff, flight 
    WHERE airlineStaff.airline_name = flight.airline_name AND DATEDIFF(depart_date,CURRENT_DATE()) <= 30 AND DATEDIFF(depart_date, CURRENT_DATE()) >= 0
    '''
    #default flight view within 30 days
	cursor.execute(query)
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row

	airp_query = '''
	SELECT airport_name
	FROM airport
	'''
	cursor.execute(airp_query)
	airp_data = cursor.fetchall()

	airpID_query = '''
	SELECT airplane_ID
	FROM airplane
	WHERE airline_name = %s
	'''
	cursor.execute(airpID_query, (airline['airline_name']))
	airpID_data = cursor.fetchall()

	cursor.close()
	return render_template('addFlight.html', flights = data, airport = airp_data, ID = airpID_data)

#Define route for adding Flights form
@app.route('/addFlightProc', methods=['GET', 'POST'])
def addFlightProc():
	#edit so that airline, airplaneID, depairp and arrairp must exist
	#add default value
	flightnum = request.form['flightnum']
	depdate = request.form['depdate']
	deptime = request.form['deptime']
	arrdate = request.form['arrdate']
	arrtime = request.form['arrtime']
	status = request.form['status']
	price = request.form['price']
	depairp = request.form['depairp']
	arrairp = request.form['arrairp']
	airplaneID = request.form['airpID']

	username = session['username']
	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s'
	cursor.execute(query, (airline['airline_name'], flightnum, depdate, deptime))
	data = cursor.fetchone()
	
	error = None

	if(data):
		#returns an error message to the html page
		error = 'Flight already exists'
		return render_template('addFlight.html', error=error)
	else:
		ins = 'INSERT INTO flight VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (airline['airline_name'], flightnum, depdate, deptime, arrdate, arrtime, status, price, depairp, arrairp, airplaneID))
		conn.commit()
		cursor.close()
		return redirect(url_for('addFlight'))
	
#Define route for change flight status
@app.route('/flightStatus')
def flightStatus():
	return render_template('flightStatus.html')

#Define route for change flight status form
@app.route('/flightStatusProc', methods=['GET', 'POST'])
def flightStatusProc():
	username = session['username']

	flightnum = request.form['flightnum']
	depdate = request.form['depdate']
	deptime = request.form['deptime']
	status = request.form['status']

	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s'
	cursor.execute(query, (airline['airline_name'], flightnum, depdate, deptime))
	data = cursor.fetchone()
	
	error = None

	if (data):
		upd = """
		UPDATE flight SET flight_status = %s
		WHERE airline_name = %s AND flight_num = %s
		AND depart_date = %s AND depart_time = %s
		"""
		cursor.execute(upd, (status, airline['airline_name'], flightnum, depdate, deptime))
		conn.commit()
		cursor.close()
		return redirect(url_for('flightStatus'))
	else:
		#returns an error message to the html page
		error = 'Flight does not exist'
		return render_template('flightStatus.html', error=error)

	return render_template('flightStatus.html')

#Define route for adding new plane
@app.route('/addPlane')
def addPlane():
	return render_template('addPlane.html')

#Define route for adding new plane form
@app.route('/addPlaneProc', methods=['GET', 'POST'])
def addPlaneProc():
	username = session['username']
	airplaneID = request.form['airplaneID']
	seat = request.form['seat']

	cursor = conn.cursor()

	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	airline = cursor.fetchone()

	query = 'SELECT * FROM airplane WHERE airline_name = %s AND airplane_ID = %s'
	cursor.execute(query, (airline['airline_name'], airplaneID))
	data = cursor.fetchone()
	
	error = None

	if (data):
		#returns an error message to the html page
		error = 'Airplane ID already exist'
		return render_template('addPlane.html', error=error)
	else:
		ins = 'INSERT INTO airplane VALUES(%s, %s, %s)'
		cursor.execute(ins, (airline['airline_name'], airplaneID, seat))
		conn.commit()
		cursor.close()
		return redirect(url_for('addPlaneConfirm', airlinename=airline['airline_name'], airplaneID=airplaneID))
	return render_template('addPlane.html')

#Define route for add plane confirmation
@app.route('/addPlaneConfirm/<airlinename>/<airplaneID>/')
def addPlaneConfirm(airlinename, airplaneID):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = '''
    SELECT *
	FROM airplane
	WHERE airline_name = %s
	'''
    #default flight view within 30 days
	cursor.execute(query, (airlinename))
	#stores the results in a variable
	data = cursor.fetchall()
	
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('addPlaneConfirm.html', plane = data, airplaneID = airplaneID)

#Define route for adding new airport
@app.route('/addAirport')
def addAirport():
	return render_template('addAirport.html')

#Define route for adding new airport form
@app.route('/addAirportProc', methods=['GET', 'POST'])
def addAirportProc():
	airport = request.form['airport']
	city = request.form['city']

	cursor = conn.cursor()
	query = 'SELECT * FROM airport WHERE airport_name = %s AND city = %s'
	cursor.execute(query, (airport, city))
	data = cursor.fetchone()
	
	error = None

	if (data):
		#returns an error message to the html page
		error = 'Airport already exist'
		return render_template('addAirport.html', error=error)
	else:
		ins = 'INSERT INTO airport VALUES(%s, %s)'
		cursor.execute(ins, (airport, city))
		conn.commit()
		cursor.close()
		return render_template('addAirport.html')
	return render_template('addAirport.html')

#Define route for view flight ratings
@app.route('/flightRatings')
def flightRatings():
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()
	query = '''
    SELECT airline_name, flight_num, depart_date, depart_time, CAST(AVG(rating) AS DECIMAL(1,0)) AS avgRating 
	FROM review WHERE airline_name = %s
	GROUP BY airline_name, flight_num, depart_date, depart_time
    '''
	cursor.execute(query, (airline['airline_name']))
	#stores the results in a variable
	data = cursor.fetchall()
	cursor.close()

	return render_template('flightRatings.html', rating = data)


#Define route for all flight ratings
@app.route('/allFlightRatings<airlinename>/<flightnum>/<depdate>/<deptime>/')
def allFlightRatings(airlinename, flightnum, depdate, deptime):
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	query = '''
    SELECT email, comment, rating
	FROM review
	WHERE airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s
	'''
    #default flight view within 30 days
	cursor.execute(query, (airlinename, flightnum, depdate, deptime))
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()
	return render_template('allFlightRatings.html', ratings = data)

#Define route for view booking agents
@app.route('/viewAgents')
def viewAgents():
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	#executes query
	month_query = '''
    SELECT MONTHNAME(purchase_date) AS month 
	FROM ticket, cust_purchases 
	WHERE cust_purchases.ticket_ID = ticket.ID AND agent_email is not NULL 
	AND YEAR(purchase_date) = YEAR(CURRENT_DATE) AND MONTH(purchase_date) < MONTH(CURRENT_DATE) 
	AND ticket.airline_name = %s
	GROUP BY MONTHNAME(purchase_date) ASC
	'''
    #default flight view within 30 days
	cursor.execute(month_query, (airline['airline_name']))
	#stores the results in a variable
	data = cursor.fetchall()

	year_query = '''
    SELECT YEAR(purchase_date) AS year 
	FROM ticket, cust_purchases 
	WHERE cust_purchases.ticket_ID = ticket.ID AND agent_email is not NULL 
	AND YEAR(purchase_date) < YEAR(CURRENT_DATE) AND ticket.airline_name = %s
	GROUP BY YEAR(purchase_date) ASC
	'''
	cursor.execute(year_query, (airline['airline_name']))
	year_data = cursor.fetchall()

	comm_query = '''
	SELECT SUM(CAST(sold_price*0.1 AS DECIMAL(10,2))) AS tot_commission, agent_email, YEAR(purchase_date) AS year 
	FROM ticket, cust_purchases 
	WHERE cust_purchases.ticket_ID = ticket.ID AND agent_email is not NULL 
	AND YEAR(purchase_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
	AND ticket.airline_name = %s
	GROUP BY agent_email, year ORDER BY tot_commission DESC
	'''
	cursor.execute(comm_query, (airline['airline_name']))
	comm = cursor.fetchall()
	cursor.close()

	return render_template('viewAgents.html', month = data, year = year_data, commission = comm)

#Define route for view monthly/yearly booking agents based on ticket sales
@app.route('/top5Agent/<crit>/<typee>/')
def top5Agent(crit, typee):
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	#executes query
	if typee == 'month':
		query = '''
    	SELECT agent_email, MONTHNAME(purchase_date) AS month, COUNT(ticket_ID) AS ticket_sales 
		FROM cust_purchases, ticket 
		WHERE cust_purchases.ticket_ID = ticket.ID AND agent_email is not NULL 
		AND YEAR(purchase_date) = YEAR(CURRENT_DATE) AND MONTH(purchase_date) < MONTH(CURRENT_DATE) 
		AND MONTHNAME(purchase_date) = %s AND ticket.airline_name = %s
		GROUP BY agent_email, MONTHNAME(purchase_date) ORDER BY ticket_sales DESC LIMIT 5
		'''
	if typee == 'year':
		query = '''
    	SELECT agent_email, YEAR(purchase_date) AS year, COUNT(ticket_ID) AS ticket_sales 
		FROM cust_purchases, ticket 
		WHERE cust_purchases.ticket_ID = ticket.ID AND agent_email is not NULL 
		AND YEAR(purchase_date) < YEAR(CURRENT_DATE)
		AND YEAR(purchase_date) = %s AND ticket.airline_name = %s
		GROUP BY agent_email, YEAR(purchase_date) ORDER BY ticket_sales DESC LIMIT 5
		'''
    #default flight view within 30 days
	cursor.execute(query, (crit, airline['airline_name']))
	#stores the results in a variable
	data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row
	cursor.close()

	return render_template('top5Agent.html', agent = data, crit = crit)

#Define route for view freq customers
@app.route('/frequentCustomers')
def frequentCustomers():
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	max_ticket_query = '''
    SELECT MAX(ticket_count) AS max_ticket FROM (
	SELECT cust_email, COUNT(ID) as ticket_count 
	FROM ticket, cust_purchases WHERE cust_purchases.ticket_ID = ticket.ID 
	AND YEAR(purchase_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
	AND ticket.airline_name = %s
	GROUP BY cust_email) AS T
	'''
	cursor.execute(max_ticket_query, (airline['airline_name']))
	#stores the results in a variable
	max_data = cursor.fetchone()

	query = '''
	SELECT cust_email, COUNT(ID) as ticket_count 
	FROM ticket, cust_purchases WHERE cust_purchases.ticket_ID = ticket.ID 
	AND YEAR(purchase_date) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 YEAR))
	AND ticket.airline_name = %s
	GROUP BY cust_email HAVING ticket_count = %s
	'''
	cursor.execute(query, (airline['airline_name'], max_data['max_ticket']) )
	#stores the results in a variable
	data = cursor.fetchall()

	cust_query = '''
	SELECT DISTINCT name, cust_purchases.cust_email AS email 
	FROM customer, cust_purchases, ticket 
	WHERE cust_purchases.ticket_ID = ticket.ID AND cust_purchases.cust_email = customer.email 
	AND ticket.airline_name = %s
	'''
	cursor.execute(cust_query, (airline['airline_name']))
	cust_data = cursor.fetchall()
	cursor.close()

	return render_template('frequentCustomers.html', customer = data, allCustomer = cust_data)

#Define route for all flights for a particular customer
@app.route('/customerFlights/<email>/')
def customerFlights(email):
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()
	
	#executes query
	key_query = '''
    SELECT DISTINCT airline_name, flight_num, depart_date, depart_time 
	FROM cust_purchases, ticket WHERE cust_purchases.ticket_ID = ticket.ID 
	AND cust_purchases.cust_email = %s AND ticket.airline_name = %s
	'''
    #default flight view within 30 days
	cursor.execute(key_query, (email, airline['airline_name']))
	#stores the results in a variable
	key_data = cursor.fetchall()
	#use fetchall() if you are expecting more than 1 data row

	query = '''
	SELECT DISTINCT flight.airline_name, flight.flight_num, flight.depart_date, flight.depart_time , 
	flight.arrive_date, flight.arrive_time, flight.flight_status, flight.base_price, 
	flight.depart_airport, flight.arrive_airport, flight.airplane_ID
	FROM cust_purchases, ticket, flight 
	WHERE ticket.airline_name = flight.airline_name AND ticket.flight_num = flight.flight_num 
	AND ticket.depart_date = flight.depart_date AND ticket.depart_time = flight.depart_time 
	AND cust_purchases.ticket_ID = ticket.ID AND cust_purchases.cust_email = %s
	AND ticket.airline_name = %s ORDER BY flight.depart_date
	'''
	cursor.execute(query, (email, airline['airline_name']))
	#stores the results in a variable
	data = cursor.fetchall()
	cursor.close()

	return render_template('customerFlights.html', flights = data)

#Define route for view Report
@app.route('/viewReports')
def viewReports():
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	year_query = '''
	SELECT YEAR(purchase_date) AS year, COUNT(ID) as ticket_sales 
	FROM ticket 
    WHERE YEAR(purchase_date) < YEAR(CURRENT_DATE)  AND airline_name = %s 
	GROUP BY YEAR(purchase_date)
	ORDER BY YEAR(purchase_date) ASC
	'''
	cursor.execute(year_query, (airline['airline_name']))
	#stores the results in a variable
	yearly = cursor.fetchall()

	month_query = '''
	SELECT MONTHNAME(purchase_date) AS month, COUNT(ID) as ticket_sales 
	FROM ticket 
    WHERE YEAR(purchase_date) = YEAR(CURRENT_DATE)  
	AND airline_name = %s GROUP BY MONTHNAME(purchase_date)
	ORDER BY MONTHNAME(purchase_date) ASC
	'''
	cursor.execute(month_query, (airline['airline_name']))
	#stores the results in a variable
	monthly = cursor.fetchall()

	for each in monthly:
		print(each['ticket_sales'])

	cursor.close()
	return render_template('viewReports.html', monthly = monthly, yearly = yearly)

#Define route for view Report date form
@app.route('/viewReportDate', methods=['GET', 'POST'])
def viewReportDate():
	username = session['username']
	startdate = request.form['startdate']
	enddate = request.form['enddate']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	query = '''
	SELECT purchase_date, COUNT(ID) as ticket_sales FROM ticket 
    WHERE purchase_date >= %s AND purchase_date <= %s AND airline_name = %s 
	GROUP BY purchase_date ORDER BY purchase_date ASC
	'''
	cursor.execute(query, (startdate, enddate, airline['airline_name']))
	data = cursor.fetchall()

	for each in data:
		print(each['purchase_date'])

	cursor.close()
	return render_template('dateChart.html', daterange = data)

#Define route for date Chart
@app.route('/dateChart')
def dateChart():
	return render_template('dateChart.html')

#Define route for view revenue
@app.route('/compareRevenue')
def compareRevenue():
	username = session['username']
	#cursor used to send queries
	cursor = conn.cursor()
	#executes query
	airline_query = '''
    SELECT airline_name
    FROM airlineStaff 
    WHERE username = %s
    '''
	cursor.execute(airline_query, (username))
	#stores the results in a variable
	airline = cursor.fetchone()

	indirect = '''
	SELECT SUM(sold_price) AS revenue FROM ticket, cust_purchases 
	WHERE cust_purchases.ticket_ID = ticket.ID AND airline_name = %s
	AND agent_email is not NULL
	'''
	cursor.execute(indirect, (airline['airline_name']))
	#stores the results in a variable
	indirect_data = cursor.fetchone()

	direct = '''
	SELECT SUM(sold_price) AS revenue FROM ticket, cust_purchases 
	WHERE cust_purchases.ticket_ID = ticket.ID AND airline_name = %s 
	AND agent_email is NULL
	'''
	cursor.execute(direct, (airline['airline_name']))
	#stores the results in a variable
	direct_data = cursor.fetchone()

	cursor.close()
	return render_template('compareRevenue.html', indirect = indirect_data, direct = direct_data)
	
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

	cursor = conn.cursor()
	query = 'SELECT * FROM bookingagent WHERE email = %s and password = MD5(%s)'
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
			SELECT DISTINCT
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

#Authenticates customer ticket purchase
@app.route('/purchaseTicketCustAuth', methods=['GET', 'POST'])
def purchaseTicketCustAuth():

	airline = request.form['airline']
	flightno = request.form['flightno']
	departdate = request.form['departdate']
	departtime = request.form['departtime']
	cardno = request.form['cardno']
	cardtype = request.form['cardtype']
	cardexp = request.form['cardexp']

	cursor = conn.cursor()
	query = """SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s AND
				(depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))
			"""
	cursor.execute(query, (airline, flightno, departdate, departtime))
	flightexists = cursor.fetchone()

	query = """SELECT
					ticketCount
				FROM
					flight
					NATURAL JOIN(
					SELECT
						airline_name, depart_date, depart_time, flight_num, COUNT(ID) AS ticketCount
					FROM
						ticket
					GROUP BY
						airline_name, depart_date, depart_time, flight_num
					) AS ticketsPerFlight
				WHERE
					flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s
			"""
	cursor.execute(query, (airline, flightno, departdate, departtime))
	flightticketsresult = cursor.fetchone()
	if (flightticketsresult is None):
		flighttickets = 0
	else:
		flighttickets = flightticketsresult['ticketCount']

	query = """
				SELECT
					seat_amount
				FROM
					flight NATURAL JOIN airplane
				WHERE
					flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s
			"""
	cursor.execute(query, (airline, flightno, departdate, departtime))
	seatamount = cursor.fetchone()

	query = 'SELECT name FROM customer WHERE email = %s'
	cursor.execute(query, (session['email']))
	name = cursor.fetchone()['name']

	query = 'SELECT * FROM flight WHERE depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME())'
	cursor.execute(query)
	data = cursor.fetchall()

	error = None
	if(not flightexists):
		error = "Flight does not exist or has already departed, please reenter flight information"
		cursor.close()
		return render_template('purchaseTicketCust.html', flights=data, error=error)
	elif(flighttickets >= seatamount['seat_amount']):
		error = "Seats are filled for that flight"
		cursor.close()
		return render_template('purchaseTicketCust.html', flights=data, error=error)
	else:
		if (flighttickets >= seatamount['seat_amount'] * decimal.Decimal('0.7')):
			ticketprice = flightexists['base_price'] * decimal.Decimal('1.2')
		else:
			ticketprice = flightexists['base_price']
		cursor.execute('SELECT MAX(ID) FROM ticket')
		ticketid = cursor.fetchone()
		if ticketid['MAX(ID)'] is None:
			ticketid['MAX(ID)'] = 0
		ticketid = str(int(ticketid['MAX(ID)']) + 1)
		ins = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, CURRENT_DATE(), CURRENT_TIME(), %s, %s, %s, %s)'
		cursor.execute(ins, (ticketid.zfill(10), ticketprice, cardno, cardtype, cardexp, name, airline, flightno, departdate, departtime))
		conn.commit()
		purchase_insert = 'INSERT INTO cust_purchases VALUES(%s, %s, NULL)'
		cursor.execute(purchase_insert,(ticketid.zfill(10), session['email']))
		conn.commit()
		cursor.close()
		return redirect(url_for('homecust'))

#Customer can leave a review for a flight
@app.route('/rateFlight')
def rateFlight():

	cursor = conn.cursor()
	query = """
			SELECT DISTINCT
				flight.airline_name, flight.flight_num, flight.depart_date, flight.depart_time, flight.arrive_date, flight.arrive_time,
				flight.flight_status, flight.base_price, flight.depart_airport, flight.arrive_airport, flight.airplane_ID
			FROM
				cust_purchases, ticket NATURAL JOIN flight
			WHERE
				cust_email = %s AND cust_purchases.ticket_ID = ticket.ID AND
				(flight.arrive_date < CURRENT_DATE() OR (flight.arrive_date = CURRENT_DATE() AND flight.arrive_time < CURRENT_TIME()))
			"""
	cursor.execute(query, session['email'])
	flightdata = cursor.fetchall()
	cursor.close()
	return render_template('rateFlight.html', flights=flightdata)

#Authenticates flight review
@app.route('/rateFlightAuth', methods=['GET', 'POST'])
def rateFlightAuth():
	airline = request.form['airline']
	flightno = request.form['flightno']
	departdate = request.form['departdate']
	departtime = request.form['departtime']
	comment = request.form['comment']
	rating = request.form['rating']
	if rating == 'one':
		numrating = 1
	elif rating == 'two':
		numrating = 2
	elif rating == 'three':
		numrating = 3
	elif rating == 'four':
		numrating = 4
	elif rating == 'five':
		numrating = 5

	cursor = conn.cursor()
	query = """
			SELECT
				*
			FROM
				cust_purchases, ticket NATURAL JOIN flight
			WHERE
				cust_email = %s AND cust_purchases.ticket_ID = ticket.ID AND
				flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s AND
				(flight.arrive_date < CURRENT_DATE() OR (flight.arrive_date = CURRENT_DATE() AND flight.arrive_time < CURRENT_TIME()))
			"""
	cursor.execute(query, (session['email'], airline, flightno, departdate, departtime))
	flightexists = cursor.fetchone()

	query = """
			SELECT DISTINCT
				flight.airline_name, flight.flight_num, flight.depart_date, flight.depart_time, flight.arrive_date, flight.arrive_time,
				flight.flight_status, flight.base_price, flight.depart_airport, flight.arrive_airport, flight.airplane_ID
			FROM
				cust_purchases, ticket NATURAL JOIN flight
			WHERE
				cust_email = %s AND cust_purchases.ticket_ID = ticket.ID AND
				(flight.arrive_date < CURRENT_DATE() OR (flight.arrive_date = CURRENT_DATE() AND flight.arrive_time < CURRENT_TIME()))
			"""
	cursor.execute(query, session['email'])
	flightdata = cursor.fetchall()

	error = None
	if(not flightexists):
		error = "Not a previously flown flight, please reenter flight information"
		cursor.close()
		return render_template('rateFlight.html', flights=flightdata, error=error)
	else:
		ins = 'INSERT INTO review VALUES(%s, %s, %s, %s, %s, %s, %s)'
		cursor.execute(ins, (session['email'], airline, flightno, departdate, departtime, comment, numrating))
		conn.commit()
		cursor.close()
		return redirect(url_for('homecust'))

#Customer can track spending history on tickets
@app.route('/trackSpending')
def trackSpending():

	cursor = conn.cursor()
	query = """
			SELECT
				SUM(sold_price) AS monthlySpending,
				MONTHNAME(purchase_date) AS month
			FROM
				cust_purchases,
				ticket
			WHERE
				cust_email = %s AND ticket_ID = ID AND purchase_date >= DATE_ADD(CURRENT_DATE, INTERVAL -6 MONTH)
			GROUP BY
				MONTH(purchase_date)
			ORDER BY
				purchase_date
			"""
	cursor.execute(query, session['email'])
	data = cursor.fetchall()
	query = """
			SELECT
				SUM(sold_price) AS totalSpending
			FROM
				cust_purchases, ticket
			WHERE
				cust_email = %s AND ticket_ID = ID AND purchase_date >= DATE_ADD(CURRENT_DATE, INTERVAL -1 YEAR)
			"""
	cursor.execute(query, session['email'])
	totalspending = cursor.fetchone()
	cursor.close()
	return render_template('trackSpending.html', total=totalspending, data=data)

#Authenticates track spending
@app.route('/trackSpendingAuth', methods=['GET', 'POST'])
def trackSpendingAuth():
	rangebegin = request.form['rangebegin']
	rangeend = request.form['rangeend']

	cursor = conn.cursor()
	query = """
			SELECT
				SUM(sold_price) AS monthlySpending,
				MONTHNAME(purchase_date) AS month
			FROM
				cust_purchases,
				ticket
			WHERE
				cust_email = %s AND ticket_ID = ID AND purchase_date >= %s AND purchase_date <= %s
			GROUP BY
				MONTH(purchase_date)
			ORDER BY
				purchase_date
			"""
	cursor.execute(query, (session['email'], rangebegin, rangeend))
	data = cursor.fetchall()
	query = """
			SELECT
				SUM(sold_price) AS totalSpending
			FROM
				cust_purchases, ticket
			WHERE
				cust_email = %s AND ticket_ID = ID AND purchase_date >= %s AND purchase_date <= %s
			"""
	cursor.execute(query, (session['email'], rangebegin, rangeend))
	totalspending = cursor.fetchone()
	cursor.close()
	return render_template('trackSpending.html', total=totalspending, data=data)

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


from datetime import date, timedelta, datetime
@app.route('/viewcommission')
def viewcommission():
	email = session['email']
	start = (date.today()-timedelta(days=30))
	end = date.today()
	cursor = conn.cursor()
	query = """SELECT sum(sold_price *.1) as sum
				   FROM cust_purchases c, ticket t
				   WHERE c.ticket_ID = t.ID AND DATEDIFF( CURRENT_DATE(),t.purchase_date) <= 30 AND email = %s"""
	cursor.execute(query, (email))
	counter = cursor.fetchone()['sum']
	if counter is None:
		counter = 0
	commission = round(counter, 2)
	query = """SELECT count(t.ID) as count
				FROM cust_purchases c, ticket t
				WHERE email = %s AND DATEDIFF(CURRENT_DATE(),t.purchase_date) <= 30 AND c.ticket_ID = t.ID"""
	cursor.execute(query,(email))
	tickets = cursor.fetchone()['count']
	if tickets == 0:
		average = 0
	else:
		average = commission/ tickets
	return render_template('viewcommission.html', commission=commission, tickets=tickets, average= average, start= start, end= end)


@app.route('/commissionSearch', methods=['POST','GET'])
def commissionSearch():
	start = request.form['startdate']
	startcounter = datetime.strptime(start, '%Y-%m-%d')
	end = request.form['enddate']
	endcounter = datetime.strptime(end, '%Y-%m-%d')
	email = session['email']
	cursor = conn.cursor()
	error = None
	if endcounter < startcounter:
		error = "Ending date before starting date"
		start = (date.today() - timedelta(days=30))
		end = date.today()
	query = """SELECT sum(sold_price *.1) as sum
				   FROM cust_purchases c, ticket t
				   WHERE c.ticket_ID = t.ID AND t.purchase_date >= %s AND t.purchase_date <= %s AND email = %s"""
	cursor.execute(query, (start, end, email))
	counter = cursor.fetchone()['sum']
	if counter is None:
		counter = 0
	commission = round(counter, 2)
	query = """SELECT count(t.ID) as count
					FROM cust_purchases c, ticket t
					WHERE email = %s AND t.purchase_date >= %s AND t.purchase_date <= %s AND c.ticket_ID = t.ID"""
	cursor.execute(query, (email, start, end))
	tickets = cursor.fetchone()['count']
	if tickets == 0 :
		average = 0
	else:
		average = commission / tickets
	return render_template('viewcommission.html', commission = commission, tickets= tickets, average= average, error= error, start= start, end= end)


@app.route("/viewmyflightsagent")
def viewmyflightsagent():
    cursor = conn.cursor()
    query = """
                SELECT DISTINCT
                    customer.name, flight.airline_name, flight.flight_num, flight.depart_date, flight.depart_time, flight.arrive_date, flight.arrive_time,
                    flight.flight_status, flight.base_price, flight.depart_airport, flight.arrive_airport, flight.airplane_ID
                FROM
                    customer, cust_purchases c, ticket NATURAL JOIN flight
                WHERE
                    c.email = %s AND c.ticket_ID = ticket.ID AND customer.email = c.cust_email AND
                    (flight.depart_date > CURRENT_DATE() OR (flight.depart_date = CURRENT_DATE() AND flight.depart_time > CURRENT_TIME()))
                """
    cursor.execute(query,(session['email']))
    data = cursor.fetchall()
    return render_template('myflightagent.html',flights= data)


@app.route('/topCustomers')
def viewtopcust():
    cursor= conn.cursor()
    query = """SELECT customer.name as name, count(ticket_ID) as count
               FROM cust_purchases c, customer, ticket t 
               WHERE %s = c.email AND c.cust_email = customer.email AND t.ID = c.ticket_ID AND
                    TIMESTAMPDIFF(MONTH, t.purchase_date, CURRENT_DATE()) <= 6
               GROUP BY customer.name
               ORDER BY count desc"""
    cursor.execute(query,(session['email']))
    labelsTicket = []
    valuesTicket = []
    count = 0
    while count < 5:
        data = cursor.fetchone()
        if data is None:
            break
        labelsTicket.append(data['name'])
        valuesTicket.append(data['count'])
        count += 1

    query = """SELECT customer.name as name, sum(sold_price)*.1 as sum
               FROM cust_purchases c, customer, ticket t
               WHERE %s = c.email AND c.cust_email = customer.email AND t.ID = c.ticket_ID AND
                    TIMESTAMPDIFF(YEAR, t.purchase_date, CURRENT_DATE()) <= 1
               GROUP BY customer.name
               ORDER BY sum desc"""
    cursor.execute(query, (session['email']))
    labelsComm = []
    valuesComm = []
    count = 0
    while count < 5:
        data = cursor.fetchone()
        if data is None:
            break
        labelsComm.append(data['name'])
        valuesComm.append(data['sum'])
        count += 1

    return render_template('viewtopcust.html', labels1= labelsTicket, values1= valuesTicket, title1="Top 5 Customers by tickets",
                           labels2= labelsComm, values2= valuesComm, title2="Top 5 Customers by commission")


# Agent ticket purchasing
@app.route('/purchaseTicketAgent')
def purchaseTicketAgent():
    cursor = conn.cursor()
    query = 'SELECT * FROM flight WHERE depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME())'
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return render_template('purchaseTicketAgent.html', flights=data)


# Authenticates customer ticket purchase
@app.route('/purchaseTicketAgentAuth', methods=['GET', 'POST'])
def purchaseTicketAgentAuth():

    airline = request.form['airline']
    flightno = request.form['flightno']
    departdate = request.form['departdate']
    departtime = request.form['departtime']
    custEmail = request.form["custemail"]
    cardno = request.form['cardno']
    cardtype = request.form['cardtype']
    cardexp = request.form['cardexp']

    cursor = conn.cursor()
    query = """SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s AND depart_date = %s AND depart_time = %s AND
                (depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME()))
            """
    cursor.execute(query, (airline, flightno, departdate, departtime))
    flightexists = cursor.fetchone()

    query = """SELECT
                    ticketCount
                FROM
                    flight
                    NATURAL JOIN(
                    SELECT
                        airline_name, depart_date, depart_time, flight_num, COUNT(ID) AS ticketCount
                    FROM
                        ticket
                    GROUP BY
                        airline_name, depart_date, depart_time, flight_num
                    ) AS ticketsPerFlight
                WHERE
                    flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s
            """
    cursor.execute(query, (airline, flightno, departdate, departtime))
    flightticketsresult = cursor.fetchone()
    if (flightticketsresult is None):
        flighttickets = 0
    else:
        flighttickets = flightticketsresult['ticketCount']

    query = """
                SELECT
                    seat_amount
                FROM
                    flight NATURAL JOIN airplane
                WHERE
                    flight.airline_name = %s AND flight.flight_num = %s AND flight.depart_date = %s AND flight.depart_time = %s
            """
    cursor.execute(query, (airline, flightno, departdate, departtime))
    seatamount = cursor.fetchone()

    query = 'SELECT name FROM customer WHERE email = %s'
    cursor.execute(query, (custEmail))
    name = cursor.fetchone()

    query = 'SELECT * FROM flight WHERE depart_date > CURRENT_DATE() OR (depart_date = CURRENT_DATE() AND depart_time > CURRENT_TIME())'
    cursor.execute(query)
    data = cursor.fetchall()

    if (not name):
        error = "Customer does not exist"
        cursor.close()
        return render_template('purchaseTicketAgent.html', flights=data, error=error)
    name = name['name']

    if(not flightexists):
        error = "Flight does not exist or has already departed, please reenter flight information"
        cursor.close()
        return render_template('purchaseTicketAgent.html', flights=data, error=error)
    elif(flighttickets >= seatamount['seat_amount']):
        error = "Seats are filled for that flight"
        cursor.close()
        return render_template('purchaseTicketAgent.html', flights=data, error=error)
    else:
        if (flighttickets >= float(seatamount['seat_amount']) * 0.7):
            ticketprice = flightexists['base_price'] * 1.2
        else:
            ticketprice = flightexists['base_price']
        cursor.execute('SELECT MAX(ID) FROM ticket')
        ticketid = cursor.fetchone()
        ticketid = str(int(ticketid['MAX(ID)']) + 1)
        ins = 'INSERT INTO ticket VALUES(%s, %s, %s, %s, %s, %s, CURRENT_DATE(), CURRENT_TIME(), %s, %s, %s, %s)'
        cursor.execute(ins, (ticketid.zfill(10), ticketprice, cardno, cardtype, cardexp, name, airline, flightno, departdate, departtime))
        conn.commit()
        purchase_insert = 'INSERT INTO cust_purchases VALUES(%s, %s, %s)'
        cursor.execute(purchase_insert,(ticketid.zfill(10),custEmail, session['email']))
        conn.commit()
        update = """UPDATE bookingagent
                    SET commission= commission + %s*.1
                    WHERE email = %s"""
        cursor.execute(update,(ticketprice,session['email']))
        conn.commit()
        cursor.close()
        return redirect(url_for('homeagent'))


#Home page for staff
@app.route('/homestaff')
def homestaff():
	username = session['username']
	cursor = conn.cursor()

	query = 'SELECT * FROM airlinestaff WHERE username = %s'
	cursor.execute(query, (username))

	userdata = cursor.fetchone()
	query = """
			SELECT DISTINCT
				arrive_airport,
				COUNT(*) AS ticketCount
			FROM
				ticket NATURAL JOIN flight
			WHERE
				purchase_date >= DATE_ADD(CURRENT_DATE, INTERVAL -3 MONTH)
			GROUP BY
				arrive_airport
			ORDER BY
				ticketCount
			DESC
			LIMIT 3
			"""
	cursor.execute(query)
	topdestsmonth = cursor.fetchall()
	query = """
			SELECT DISTINCT
				arrive_airport,
				COUNT(*) AS ticketCount
			FROM
				ticket NATURAL JOIN flight
			WHERE
				purchase_date >= DATE_ADD(CURRENT_DATE, INTERVAL -1 YEAR)
			GROUP BY
				arrive_airport
			ORDER BY
				ticketCount
			DESC
			LIMIT 3
			"""
	cursor.execute(query)
	topdestsyear = cursor.fetchall()
	
	query = '''
    SELECT * 
    FROM flight 
    WHERE flight.airline_name = %s AND DATEDIFF(depart_date,CURRENT_DATE()) <= 30 
	AND DATEDIFF(depart_date, CURRENT_DATE()) >= 0
    '''
    #default flight view within 30 days
	cursor.execute(query, (userdata['airline_name']))
	#stores the results in a variable
	flights_data = cursor.fetchall()

	cursor.close()
	
	return render_template('homestaff.html', airlinestaff=userdata, topdestsmonth=topdestsmonth, topdestsyear=topdestsyear, flights = flights_data)


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
		id = str(int(id['MAX(booking_agent_ID)']) + 1)
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
@app.route('/logoutCust')
def logoutCust():
    session.pop('email')
    return redirect('/logincust')

@app.route('/logoutAgent')
def logoutAgent():
    session.pop('email')
    return redirect('/loginagent')

#Logout for staff
@app.route('/logoutusername')
def logoutusername():
    session.pop('username')
    return redirect('/loginstaff')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
