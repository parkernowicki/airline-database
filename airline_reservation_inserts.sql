/*airline*/
insert into airline values ('China Eastern');
/*airport*/
insert into airport values ('JFK', 'NYC');
insert into airport values ('PVG', 'Shanghai');
insert into airport values ('ICN', 'Seoul');
/*customer*/
insert into customer values ('joe.cameron@gmail.com', 'Joe Cameron', MD5('joe123'), 
'12', 'Aspen Court', 'Boston', 'Massachusetts', '6174375760', '171384112', 
'2023-09-02', 'United States', '1994-12-20');
insert into customer values ('nathan.harris@gmail.com', 'Nathan Harris', MD5('pass456'), 
'1417', 'Kelly Street', 'Charlotte', 'North Carolina', '7042223261', '369755361', 
'2025-03-16', 'United States', '1971-01-17');
/*booking agent*/
insert into BookingAgent values ('kayak@gmail.com',MD5('kayakflight23'),'23567', NULL);
insert into BookingAgent values ('googleflights@gmail.com',MD5('google'),'67543', NULL);
/*airplane*/
insert into airplane values ('China Eastern', '45678', 200);
insert into airplane values ('China Eastern', '12121', 150);
/*airlineStaff*/
insert into airlineStaff values ('katsierra', MD5('kat12sie'), 'Katie', 'Sierra', 
'1997-07-20', 'China Eastern');
/*staffPhone*/
insert into staffPhone values ('katsierra', '2025550114');
/*flight*/
insert into flight values ('China Eastern', '66678', '2020-12-02', '19:00:00', 
'2020-12-03', '08:30:00', 'on-time', 750.00,'PVG', 'JFK', '45678');
insert into flight values ('China Eastern', '12345', '2020-08-01', '11:00:00', 
'2020-08-01', '14:30:00', 'on-time', 200.00, 'ICN', 'PVG', '45678');
insert into flight values ('China Eastern', '44669', '2021-08-01', '08:00:00', 
'2021-08-01', '12:00:00', 'delayed', 500.00, 'PVG', 'ICN', '12121');
/*ticket*/
insert into ticket values ('00045', 750.00, '4024007152284807', 'credit', '2023-09-01', 
'Joe Cameron', '2020-11-02', '08:00:00', 'China Eastern', '66678', '2020-12-02', '19:00:00');
insert into ticket values ('01234', 280.00, '5356666795790424', 'debit', '2022-02-01', 
'Nathan Harris', '2021-03-20', '18:45:00', 'China Eastern', '44669', '2021-08-01', '08:00:00');
insert into ticket values ('11111', 100.00, '5356666795790424', 'debit', '2022-02-01', 
'Nathan Harris', '2020-11-02', '9:45:00', 'China Eastern', '12345', '2020-08-01', '11:00:00');
insert into ticket values ('22222', 170.00, '5356666795790424', 'debit', '2022-02-01', 
'Nathan Harris', '2020-11-02', '10:45:00', 'China Eastern', '66678', '2020-12-02', '19:00:00');
/*cust_purchases*/
insert into cust_purchases values ('00045', 'joe.cameron@gmail.com', 'kayak@gmail.com'); /* change end value*/
insert into cust_purchases values ('01234', 'nathan.harris@gmail.com', NULL);
insert into cust_purchases values ('11111', 'nathan.harris@gmail.com', 'kayak@gmail.com');
insert into cust_purchases values ('22222', 'nathan.harris@gmail.com', 'googleflights@gmail.com');
