create table airline(
    airline_name	varchar(20),
    primary key(airline_name)
);

create table airlineStaff(
    username	varchar(10),
    user_password	varchar(32),
    first_name	varchar(20),
    last_name	varchar(20),
    dob	date,
    airline_name	varchar(20),
    primary key (username),
    foreign key (airline_name) references airline(airline_name)
);

create table staffPhone(
    username	varchar(10),
    phone_number    varchar(15),
    primary key (username, phone_number),
    foreign key (username) references airlineStaff(username)
);

create table airplane(
    airline_name   varchar(20),
    airplane_ID  varchar(5),
    seat_amount numeric(4,0),
    primary key (airline_name, airplane_ID),
    foreign key (airline_name) references airline(airline_name),
    index(airplane_ID)
);

create table airport(
    airport_name    varchar(20),
    city    varchar(20),
    primary key (airport_name)
);

create table flight(
    airline_name    varchar(20),
    flight_num  varchar(5),
    depart_date date,
    depart_time time,
    arrive_date date,
    arrive_time time,
    flight_status   varchar(10)
        check (flight_status in ('on-time', 'delayed', 'cancelled')),
    base_price  numeric(10,2),
    depart_airport  varchar(20),
    arrive_airport  varchar(20),
    airplane_ID varchar(5) not null,
    primary key (airline_name, flight_num, depart_date, depart_time),
    foreign key (airline_name) references airline(airline_name), 
    foreign key (airplane_ID) references airplane(airplane_ID),
    foreign key (depart_airport) references airport(airport_name),
    foreign key (arrive_airport) references airport(airport_name)
);


create table ticket(
    ID  varchar(10),
    sold_price  numeric(10,2),
    card_number varchar(16),
    card_type   varchar(10) check (card_type in ('debit', 'credit')),
    expiration_date date,
    card_name   varchar(20),
    purchase_date   date,
    purchase_time   time,
    airline_name    varchar(20),
    flight_num  varchar(5),
    depart_date date,
    depart_time time,
    primary key (ID),
    foreign key (airline_name, flight_num, depart_date, depart_time) references 
    flight (airline_name, flight_num, depart_date, depart_time) 
    on delete cascade on update cascade
);

create table customer(
    email   varchar(50),
    name   varchar(20),
    password   varchar(32),
    building_number varchar(4),
    street  varchar(20),
    city    varchar(20),
    state  varchar(20),
    phone_number    varchar(15),
    passport_number varchar(9),
    passport_expiration date,
    passport_country    varchar(20),
    dob date,
    primary key (email)
);

create table BookingAgent(
    email   varchar(50),
    password  varchar(32),
    booking_agent_ID    varchar(5),
    commission  numeric(10,2),
    primary key (email)
);

create table cust_purchases(
    ticket_ID   varchar(10),
    cust_email  varchar(50),
    agent_email  varchar(50) , /* change  value with size*/
    primary key (ticket_ID, cust_email), 
    foreign key (ticket_ID) references ticket(ID),
    foreign key (cust_email) references customer(email),
    foreign key (agent_email) references BookingAgent(email) /* change  value with size*/
);

create table review(
    email   varchar(50),
    airline_name    varchar(20),
    flight_num  varchar(5),
    depart_date date,
    depart_time time,
    comment varchar(300),
    rating  numeric(1,0) check (rating <= 5 and rating >= 1),
    primary key (email, airline_name, flight_num, depart_date, depart_time),
    foreign key (email) references customer(email),
    foreign key (airline_name, flight_num, depart_date, depart_time)
    references flight(airline_name, flight_num, depart_date, depart_time)
    on delete cascade on update cascade
);
