# streamlit run "c:\Users\hp\vscode\python And LIbraries\TTMS\main.py"
# run above command

import mysql.connector
import streamlit as st
import pandas as pd
import datetime
import hashlib
import time

if 'sess' not in st.session_state:
    st.session_state['sess'] = False

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "mM10032003@#$",
    database = "TTMS"
)
mycursor = mydb.cursor()
print("connection establised")

def auth():
    
    st.set_page_config(layout="centered")
    
    st.title("Welcome to IRCTC RailConnect")

    tabs = st.tabs(["Sign In", "Sign Up"])

    with tabs[0]:
        
        st.subheader("Log In to Your Account")

        email_id = st.text_input("Email", key="login_email")
        
        password = st.text_input("Password", type="password", key="login_password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest() if password else None

        if st.button("Login"):

            query = "SELECT * FROM User WHERE email_id = %s AND user_password = %s"
            mycursor.execute(query, (email_id, hashed_password))
            
            user = mycursor.fetchone()

            if user:
                
                st.success("Logged in successfully!")
                
                st.session_state['sess'] = True
                
                st.session_state['user'] = {
                    "email_id": user[0],
                    "user_name": user[1],
                    "age": user[2],
                    "gender": user[3],
                    "mobile_no": user[5]
                }
                
                if 'booking_in_progress' not in st.session_state:
                    st.session_state.booking_in_progress = False
                    
                if 'selected_train_no' not in st.session_state:
                    st.session_state.selected_train_no = None
                    
                if 'num_tickets' not in st.session_state:
                    st.session_state.num_tickets = 1
                    
                if 'passenger_details' not in st.session_state:
                    st.session_state.passenger_details = []
                    
                if 'boarding_station' not in st.session_state:
                    st.session_state.boarding_station = None
                    
                if 'destination_station' not in st.session_state:
                    st.session_state.destination_station = None
                    
                if 'boarding_station_code' not in st.session_state:
                    st.session_state.boarding_station_code = None
                    
                if 'destination_station_code' not in st.session_state:
                    st.session_state.destination_station_code = None
                    
                if 'selected_class' not in st.session_state:
                    st.session_state.selected_class = None
                    
                if 'selected_quota' not in st.session_state:
                    st.session_state.selected_quota = None
                    
                if 'journey_date' not in st.session_state:
                    st.session_state.journey_date = datetime.datetime.now().date()
                    
                st.rerun()
                
            else:
                st.error("Incorrect email or password. Please try again.")

    with tabs[1]:

        st.subheader("Create a New Account")

        email_id = st.text_input("Email", key="signup_email")
        
        user_name = st.text_input("Username", key="signup_username")
        
        age = st.number_input("Age", min_value=1, step=1, key="signup_age")
        
        gender = st.selectbox("Gender", ["M", "F", "Other"], key="signup_gender")
        
        password = st.text_input("Password", type="password", key="signup_password")
        
        mobile_no = st.text_input("Mobile Number", key="signup_mobile")

        hashed_password = hashlib.sha256(password.encode()).hexdigest() if password else None

        if st.button("Sign Up"):

            mycursor.execute("SELECT * FROM User WHERE email_id = %s", (email_id,))
            
            existing_user = mycursor.fetchone()

            if existing_user:
                st.error("An account with this email already exists. Please log in.")
                
            elif not all([email_id, user_name, age, gender, password, mobile_no]):
                st.error("Please fill in all the fields.")
                
            else:
                query = """
                INSERT INTO User (email_id, user_name, age, gender, user_password, mobile_no)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                mycursor.execute(query, (email_id, user_name, age, gender, hashed_password, mobile_no))
                mydb.commit()
                
                st.success("Account created successfully! Please log in.")

def get_station_list():
    query = "SELECT station_code, station_name FROM Station"
    mycursor.execute(query)
    stations = mycursor.fetchall()
    return [(None, None)]+[(f"{station_name} ({station_code})", station_code) for station_code, station_name in stations]

def get_quota_list():
    query = "SELECT quota_code, quota_name FROM Quota"
    mycursor.execute(query)
    quotas = mycursor.fetchall()
    return [(None, None)]+[(f"{quota_name} ({quota_code})", quota_code) for quota_code, quota_name in quotas]

def get_class_list():
    query = "SELECT class_code, class_name FROM Class"
    mycursor.execute(query)
    classes = mycursor.fetchall()
    return [(None, None)] + [(f"{class_name} ({class_code})", class_code) for class_code, class_name in classes]

def Search_Trains(boarding_station, destination_station, journey_date):

    day_of_week = journey_date.strftime('%A')
    print(day_of_week)

    query = """
    SELECT DISTINCT t.train_no, 
                    t.train_name,
                    r1.departure_time AS boarding_departure_time,
                    DATE_ADD(%s, INTERVAL r1.day_num - 1 DAY) AS boarding_date,
                    r2.arrival_time AS destination_arrival_time,
                    DATE_ADD(%s, INTERVAL r2.day_num - 1 DAY) AS destination_date
    FROM Train t
    JOIN Route r1 ON t.train_no = r1.train_no
    JOIN Route r2 ON t.train_no = r2.train_no
    JOIN Schedule s ON t.train_no = s.train_no
    WHERE r1.station_code = %s
      AND r2.station_code = %s
      AND r1.dist_from_source < r2.dist_from_source
      AND s.day_of_week = %s;
    """
    
    mycursor.execute(query, (journey_date, journey_date, boarding_station, destination_station, day_of_week))
    
    result = mycursor.fetchall()
    column_names = [desc[0] for desc in mycursor.description]
    df = pd.DataFrame(result, columns=column_names)
        
    if 'boarding_departure_time' in df.columns:
        df['boarding_departure_time'] = df['boarding_departure_time'].astype(str)
    
    if 'destination_arrival_time' in df.columns:
        df['destination_arrival_time'] = df['destination_arrival_time'].astype(str)

    if 'boarding_departure_time' in df.columns:
        df['boarding_departure_time'] = df['boarding_departure_time'].apply(lambda x: x.split(' ')[-1][:5])

    if 'destination_arrival_time' in df.columns:
        df['destination_arrival_time'] = df['destination_arrival_time'].apply(lambda x: x.split(' ')[-1][:5])
    
    return df

def find_route():
    
    st.header("Train Routes")
    
    train_no = st.number_input(
        "Insert a train number", value=0, min_value=0, step=1, format="%d"
    )
    st.write("Train Number:", train_no)
    
    if st.button("See Route"):       
        
        query = "SELECT * FROM Route WHERE train_no = %s ORDER BY dist_from_source"
        mycursor.execute(query, (train_no,))         
        route = mycursor.fetchall()
        
        column_names = [desc[0] for desc in mycursor.description]
        
        route_df = pd.DataFrame(route, columns=column_names)

        if 'arrival_time' in route_df.columns:
            route_df['arrival_time'] = route_df['arrival_time'].astype(str).apply(lambda x: x.split(' ')[-1][:5])

        if 'departure_time' in route_df.columns:
            route_df['departure_time'] = route_df['departure_time'].astype(str).apply(lambda x: x.split(' ')[-1][:5])

        st.dataframe(route_df, use_container_width=True)
        
def handle_payment(train_no):
    try:
        mycursor = mydb.cursor(buffered=True)
        
        query_ticket = """
        SELECT ticket_id FROM Ticket
        WHERE boarding_st = %s AND destination_st = %s
        AND class_code = %s AND quota_code = %s
        """
        mycursor.execute(query_ticket, (
            st.session_state.boarding_station_code,
            st.session_state.destination_station_code,
            st.session_state.class_code,
            st.session_state.quota_code
        ))
        ticket_id_row = mycursor.fetchone()

        if not ticket_id_row:
            st.error("No ticket available for the selected criteria.")
            return

        ticket_id = ticket_id_row[0]
        
        query_fare = "SELECT fare FROM Fare WHERE ticket_id = %s"
        mycursor.execute(query_fare, (ticket_id,))
        fare_row = mycursor.fetchone()

        if not fare_row:
            st.error("Fare not found for the selected ticket.")
            return

        fare = fare_row[0]
        total_fare = fare * st.session_state.num_tickets

        st.header("Complete Your Payment")
        
        st.subheader("Journey Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**From:** {st.session_state.boarding_station}")
            st.write(f"**Train No:** {train_no}")
            st.write(f"**Class:** {st.session_state.selected_class}")
        with col2:
            st.write(f"**To:** {st.session_state.destination_station}")
            st.write(f"**Date:** {st.session_state.journey_date}")
            st.write(f"**Quota:** {st.session_state.selected_quota}")
        with col3:
            st.write(f"**Passengers:** {st.session_state.num_tickets}")
            st.write(f"**Fare per ticket:** ₹{fare:.2f}")
            st.write(f"**Total Amount:** ₹{total_fare:.2f}")

        st.divider()
        
        st.subheader("Payment Details")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pin = st.text_input("Enter your account PIN", type="password")
            st.write("")
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            
            with col_btn2:
                
                if st.button("Pay Now", type="primary"):

                    hashed_pin = hashlib.sha256(pin.encode()).hexdigest() if pin else None
                    query_pin = "SELECT account_password FROM Wallet WHERE user_id = %s"
                    mycursor.execute(query_pin, (st.session_state.user["email_id"],))
                    stored_pin_row = mycursor.fetchone()

                    if not stored_pin_row or stored_pin_row[0] != hashed_pin:
                        st.error("Incorrect PIN. Please try again.")
                        return

                    query_balance = "SELECT balance FROM Wallet WHERE user_id = %s"
                    mycursor.execute(query_balance, (st.session_state.user["email_id"],))
                    balance_row = mycursor.fetchone()

                    if balance_row is None or balance_row[0] < total_fare:
                        st.error("Insufficient balance in wallet.")
                        return

                    try:
                        mydb.rollback()
                        
                        mydb.start_transaction()

                        query_update_balance = "UPDATE Wallet SET balance = balance - %s WHERE user_id = %s"
                        mycursor.execute(query_update_balance, (total_fare, st.session_state.user["email_id"]))

                        query_transfer_money = "UPDATE Wallet SET balance = balance + %s WHERE user_id = %s"
                        mycursor.execute(query_transfer_money, (total_fare, "IRCTC@irctc.in"))
                        
                        query_insert_reservation = """
                        INSERT INTO Reservation (user_id, ticket_id, date_of_journey, num_tickets)
                        VALUES (%s, %s, %s, %s)
                        """
                        mycursor.execute(query_insert_reservation, (
                            st.session_state.user["email_id"],
                            ticket_id,
                            st.session_state.journey_date,
                            st.session_state.num_tickets
                        ))
                        pnr_no = mycursor.lastrowid

                        query_insert_payment = """
                        INSERT INTO Payment (pnr_no, user_id, date_of_payment, payment_amount) 
                        VALUES (%s, %s, %s, %s)
                        """
                        mycursor.execute(query_insert_payment, (
                            pnr_no,
                            st.session_state.user["email_id"],
                            datetime.datetime.now().date(),
                            total_fare
                        ))

                        query_seats = """
                            SELECT s.seat_id, s.stype_code, c.coach_no, s.seat_no
                            FROM Seat s
                            JOIN Coach c ON s.coach_no = c.coach_no
                            JOIN Availability a ON s.seat_id = a.seat_id
                            WHERE s.train_no = %s
                            AND c.class_id = %s
                            AND s.quota_code = %s
                            AND a.journey_date = %s
                            AND a.isAvailable = TRUE
                            LIMIT %s;
                        """
                        mycursor.execute(query_seats, (
                            train_no,
                            st.session_state.class_code,
                            st.session_state.quota_code,
                            st.session_state.journey_date,
                            st.session_state.num_tickets
                        ))
                        available_seats = mycursor.fetchall()
                        print(available_seats)
                        pax_no = 1
                        for seat in available_seats:
                            seat_id, stype, coach_no, seat_no = seat

                            query_insert_passenger = """
                            INSERT INTO Passenger (pnr_no, pax_name, pax_gender, pax_age, seat_id, status_code)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            """
                            mycursor.execute(query_insert_passenger, (
                                pnr_no,
                                st.session_state.passenger_details[pax_no - 1]["name"],
                                st.session_state.passenger_details[pax_no - 1]["gender"],
                                st.session_state.passenger_details[pax_no - 1]["age"],
                                seat_id,
                                'CNF'
                            ))

                            query_update_seat = "UPDATE Availability SET isAvailable = FALSE WHERE seat_id = %s AND journey_date = %s"
                            mycursor.execute(query_update_seat, (seat_id, st.session_state.journey_date))

                            pax_no += 1

                        if pax_no <= st.session_state.num_tickets:
                            for i in range(pax_no, st.session_state.num_tickets + 1):
                                query_insert_passenger = """
                                INSERT INTO Passenger (pnr_no, pax_name, pax_gender, pax_age, seat_id, status_code)
                                VALUES (%s, %s, %s, %s, NULL, %s)
                                """
                                mycursor.execute(query_insert_passenger, (
                                    pnr_no,
                                    st.session_state.passenger_details[i - 1]["name"],
                                    st.session_state.passenger_details[i - 1]["gender"],
                                    st.session_state.passenger_details[i - 1]["age"],
                                    'WL'
                                ))

                        mydb.commit()
                        st.success(f"Booking successful! Your PNR is {pnr_no}")
                        time.sleep(2)
                        st.session_state.booking_in_progress = False
                        st.session_state.payment_in_progress = False
                        st.rerun()

                    except Exception as e:

                        mydb.rollback()
                        st.error(f"An error occurred during payment: {str(e)}")
                        return
            
            with col_btn3:
                if st.button("Cancel"):

                    mydb.rollback()
                    st.session_state.booking_in_progress = False
                    st.session_state.payment_in_progress = False
                    st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    

def render_booking_form(train_no, num_tickets):
    if 'payment_in_progress' not in st.session_state:
        st.session_state.payment_in_progress = False
        
    if st.session_state.payment_in_progress:
        handle_payment(train_no)
        return
    
    st.header(f"Booking Form for Train No: {train_no}")
    
    st.write(f"Number of tickets: {num_tickets}")
    
    for i in range(num_tickets):
        st.write(f"### Passenger {i + 1}")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.passenger_details[i]["name"] = st.text_input(
                "Name", 
                value=st.session_state.passenger_details[i]["name"],
                key=f"name_{i}_{train_no}"
            )
        
        with col2:
            st.session_state.passenger_details[i]["gender"] = st.selectbox(
                "Gender", 
                ["Select Gender", "M", "F", "Other"], 
                key=f"gender_{i}_{train_no}"
            )
        
        with col3:
            st.session_state.passenger_details[i]["age"] = st.number_input(
                "Age",
                min_value=0, 
                max_value=120,
                value=st.session_state.passenger_details[i]["age"] if st.session_state.passenger_details[i]["age"] > 0 else 0,
                step=1,
                key=f"age_{i}_{train_no}"
            )
    
    st.write("\n")
    st.write("\n")
    st.write("\n")
    
    col1, col2 = st.columns([2,16])
    
    with col1:
        if st.button("Proceed to Pay", key=f"submit_{train_no}", type="primary"):
            if all(
                p["name"] and p["gender"] != "Select Gender" and p["age"] is not None and p["age"] > 0
                for p in st.session_state.passenger_details
            ):
                st.session_state.payment_in_progress = True
                st.rerun()
            else:
                st.error("Please fill in all passenger details.")
    
    with col2:
        if st.button("Cancel", key=f"cancel_{train_no}"):
            st.session_state.booking_in_progress = False
            st.session_state.selected_train_no = None
            st.session_state.passenger_details = []
            st.rerun()
            
def cancellation_queries(pax_id, user_id):
    mycursor = mydb.cursor(dictionary=True)

    try:
        # Start a transaction
        mydb.rollback()
        mydb.start_transaction()

        # Step 1: Check if journey date has passed
        check_journey_date_query = """
        SELECT r.date_of_journey
        FROM Passenger p
        JOIN Reservation r ON p.pnr_no = r.pnr_no
        WHERE p.pax_id = %s
        """
        mycursor.execute(check_journey_date_query, (pax_id,))
        journey_date_record = mycursor.fetchone()

        if not journey_date_record:
            st.error("Error: Journey details not found!")
            return False

        journey_date = journey_date_record['date_of_journey']
        if journey_date < datetime.date.today():
            st.error("Cancellation not allowed after the journey date.")
            return False

        # Step 2: Check current status of the passenger
        check_status_query = """
        SELECT status_code FROM Passenger WHERE pax_id = %s
        """
        mycursor.execute(check_status_query, (pax_id,))
        passenger_status = mycursor.fetchone()

        if not passenger_status:
            st.error("Passenger not found!")
            return False

        if passenger_status['status_code'] == 'CAN':
            st.error("This passenger's booking has already been cancelled.")
            return False

        # Step 3: Fetch payment details
        query_payment = """
        SELECT p.payment_amount, r.num_tickets, ps.seat_id
        FROM Payment p
        JOIN Passenger ps ON p.pnr_no = ps.pnr_no
        JOIN Reservation r ON p.pnr_no = r.pnr_no
        WHERE ps.pax_id = %s
        """
        mycursor.execute(query_payment, (pax_id,))
        payment = mycursor.fetchone()

        if not payment:
            st.error("Error: Payment details not found!")
            return False

        total_payment = float(payment['payment_amount'])
        num_tickets = int(payment['num_tickets'])

        if num_tickets <= 0:
            st.error("Error: Invalid number of passengers!")
            return False

        single_ticket_cost = total_payment / num_tickets
        refund_amount = round(single_ticket_cost * 0.8, 2)

        # Step 4: Update passenger status to "Cancelled"
        update_passenger_query = """
        UPDATE Passenger
        SET status_code = 'CAN'
        WHERE pax_id = %s
        """
        mycursor.execute(update_passenger_query, (pax_id,))

        # Step 5: Update user wallet and IRCTC wallet
        update_wallet_query = """
        UPDATE Wallet
        SET balance = balance + %s
        WHERE user_id = %s
        """
        mycursor.execute(update_wallet_query, (refund_amount, user_id))

        update_irctc_wallet_query = """
        UPDATE Wallet
        SET balance = balance - %s
        WHERE user_id = %s
        """
        mycursor.execute(update_irctc_wallet_query, (refund_amount, "IRCTC@irctc.in"))

        # Step 6: Record cancellation
        insert_cancellation_query = """
        INSERT INTO Cancellation (pax_id, refund_amount, date_of_cancellation)
        VALUES (%s, %s, %s)
        """
        date_of_cancellation = datetime.date.today()
        mycursor.execute(insert_cancellation_query, (pax_id, refund_amount, date_of_cancellation))

        # Step 7: Free the seat and update waitlist
        freed_seat_id = payment['seat_id']
        if freed_seat_id:
            waitlist_query = """
            SELECT p.pax_id
            FROM Passenger p
            JOIN Reservation r ON p.pnr_no = r.pnr_no
            WHERE p.status_code = 'WL'
            ORDER BY r.pnr_no ASC
            LIMIT 1
            """
            mycursor.execute(waitlist_query)
            waitlisted_passenger = mycursor.fetchone()

            if waitlisted_passenger:
                waitlisted_pax_id = waitlisted_passenger['pax_id']
                assign_seat_query = """
                UPDATE Passenger
                SET seat_id = %s, status_code = 'CNF'
                WHERE pax_id = %s
                """
                mycursor.execute(assign_seat_query, (freed_seat_id, waitlisted_pax_id))
            else:
                free_seat_query = """
                UPDATE Availability
                SET isAvailable = 1
                WHERE seat_id = %s
                """
                mycursor.execute(free_seat_query, (freed_seat_id,))

        # Commit transaction
        mydb.commit()
        st.success(f"Passenger {pax_id} cancellation successful. Refund of ₹{refund_amount} has been credited.")
        return True

    except Exception as e:
        mydb.rollback()
        st.error(f"An error occurred: {e}")
        return False

    finally:
        mycursor.close()

def show_bookings():
    query = """
        SELECT 
            r.pnr_no, r.user_id, r.date_of_journey, r.num_tickets,
            p.pax_id, p.pax_name, p.pax_gender, p.pax_age, p.status_code,
            s.train_no, s.coach_no, s.seat_no, s.stype_code,
            t.train_name,
            r1.station_code as boarding_station, r1.departure_time as departure_time,
            r2.station_code as destination_station, r2.arrival_time as arrival_time,
            st1.station_name as boarding_station_name,
            st2.station_name as destination_station_name
        FROM Reservation r
        JOIN Passenger p ON r.pnr_no = p.pnr_no
        LEFT JOIN Seat s ON p.seat_id = s.seat_id
        JOIN Ticket tk ON r.ticket_id = tk.ticket_id
        JOIN Train t ON s.train_no = t.train_no
        JOIN Route r1 ON tk.boarding_st = r1.station_code AND t.train_no = r1.train_no
        JOIN Route r2 ON tk.destination_st = r2.station_code AND t.train_no = r2.train_no
        JOIN Station st1 ON r1.station_code = st1.station_code
        JOIN Station st2 ON r2.station_code = st2.station_code
        WHERE r.user_id = %s
        ORDER BY r.pnr_no DESC
    """
    
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute(query, (st.session_state.user["email_id"],))
    bookings = mycursor.fetchall()

    grouped_bookings = {}
    for booking in bookings:
        pnr_no = booking['pnr_no']
        if pnr_no not in grouped_bookings:
            grouped_bookings[pnr_no] = []
        grouped_bookings[pnr_no].append(booking)

    for pnr_no, passengers in grouped_bookings.items():
        with st.container():
            reservation = passengers[0]
            
            st.markdown(f"### PNR No.- {pnr_no} | {reservation['train_name']} ({reservation['train_no']})")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"**From:** {reservation['boarding_station_name']} ({reservation['boarding_station']})")
                departure_seconds = int(reservation['departure_time'].total_seconds())
                departure_hours = departure_seconds // 3600
                departure_minutes = (departure_seconds % 3600) // 60
                departure_time = f"{departure_hours:02d}:{departure_minutes:02d}"
                st.markdown(f"**Departure:** {departure_time}")
                
            with col2:
                st.markdown(f"**To:** {reservation['destination_station_name']} ({reservation['destination_station']})")
                arrival_seconds = int(reservation['arrival_time'].total_seconds())
                arrival_hours = arrival_seconds // 3600
                arrival_minutes = (arrival_seconds % 3600) // 60
                arrival_time = f"{arrival_hours:02d}:{arrival_minutes:02d}"
                st.markdown(f"**Arrival:** {arrival_time}")
                
            with col3:
                st.markdown(f"**Journey Date:** {reservation['date_of_journey']}")
                st.markdown(f"**Total Passengers:** {reservation['num_tickets']}")

            st.markdown("___")

            cols = st.columns([2, 1, 1, 2, 2, 2, 2])
            headers = ["Name", "Gender", "Age", "Seat", "Type", "Status", "Action"]
            for col, header in zip(cols, headers):
                col.markdown(f"**{header}**")

            for passenger in passengers:
                
                cols = st.columns([2, 1, 1, 2, 2, 2, 2])
                
                cols[0].write(passenger['pax_name'])
                cols[1].write(passenger['pax_gender'])
                cols[2].write(passenger['pax_age'])
                
                seat_display = f"{passenger['coach_no']}-{passenger['seat_no']}" if passenger['coach_no'] and passenger['seat_no'] else 'Not Assigned'
                cols[3].write(seat_display)
                
                cols[4].write(passenger['stype_code'] if passenger['stype_code'] else 'N/A')
                

                status = passenger['status_code']
                if status == 'CNF':
                    cols[5].markdown(f"🟩 **{status}**")
                elif status == 'WL':
                    cols[5].markdown(f"🟨 **{status}**")
                elif status == 'CAN':
                    cols[5].markdown(f"🟥 **{status}**")
                else:
                    cols[5].write(status)

                if cols[6].button(f"Cancel", key=f"{pnr_no}_{passenger['pax_id']}"):
                    # Set the selected pax_id in session state
                    st.session_state["cancel_pax_id"] = passenger['pax_id']
                    st.session_state["user_id"] = st.session_state.user["email_id"]

                # Check if cancellation action is triggered
                if "cancel_pax_id" in st.session_state:
                    try:
                        cancellation_queries(st.session_state["cancel_pax_id"], st.session_state["user_id"])
                        del st.session_state["cancel_pax_id"]  # Clear the action once done
                    except Exception as e:
                        st.error(f"Error during cancellation: {e}")


            st.markdown("___")
            st.markdown("___")

    mycursor.close()

        
def app():
    st.set_page_config(layout="wide")

    nav1, nav2, nav3 = st.columns([12,1,1])

    with nav1:
        st.title("IRCTC RailConnect")

    with nav2:
        st.write("")
        st.button("Refresh")

    with nav3:
        st.write("")
        if st.button("Log out"):
            st.session_state.clear()
            st.rerun()

    tabs = st.tabs(["Book Tickets", "Train Routes", "My bookings"])

    with tabs[0]:
        def start_booking(train_no, num_tickets):
            st.session_state.booking_in_progress = True
            st.session_state.selected_train_no = train_no
            st.session_state.num_tickets = num_tickets
            st.session_state.passenger_details = [
                {"name": "", "gender": "M", "age": 0} for _ in range(num_tickets)
            ]
            st.write("Booking started for train:", train_no)

        if st.session_state.booking_in_progress:
            render_booking_form(st.session_state.selected_train_no, st.session_state.num_tickets)
            return

        st.write("\n")
        
        col1, col2, col3 = st.columns(3)
        station_options = get_station_list()
        station_display_names = [option[0] for option in station_options]

        with col1:
            bs = st.selectbox("**Select boarding station**", station_display_names)
            if bs:
                st.session_state.boarding_station = bs
                st.session_state.boarding_station_code = next(
                    code for name, code in station_options if name == st.session_state.boarding_station
                )

        with col2:
            st.markdown("<h1 style='text-align: center;'>➔</h1>", unsafe_allow_html=True)

        with col3:
            ds = st.selectbox("**Select destination station**", station_display_names)
            if ds:
                st.session_state.destination_station = ds
                st.session_state.destination_station_code = next(
                    code for name, code in station_options if name == st.session_state.destination_station
                )

        st.divider()

        col_s2_1, col_s2_2 = st.columns(2)

        with col_s2_1:
            
            class_options = get_class_list()
            class_display_names = [option[0] for option in class_options]

            sel_class = st.selectbox("**Select Class**", class_display_names)
            if sel_class:
                st.session_state.selected_class = sel_class
                st.session_state.class_code = next(
                    code for name, code in class_options if name == st.session_state.selected_class
                )
                
            st.write("\n")
            st.write("\n")

            st.session_state.journey_date = st.date_input(
                "**Select Travel Date**",
                st.session_state.journey_date,
                min_value=datetime.datetime.now().date(),
            )

        with col_s2_2:
            
            quota_options = get_quota_list()
            quota_display_names = [option[0] for option in quota_options]

            quota = st.selectbox("**Select Quota**", quota_display_names)
            if quota:
                st.session_state.selected_quota = quota
                st.session_state.quota_code = next(
                    code for name, code in quota_options if name == st.session_state.selected_quota
                )
                
            st.write("\n")
            st.write("\n")

            st.session_state.num_tickets = st.slider(
                "**Select Number of Tickets to Book**", 1, 6, st.session_state.num_tickets
            )

        st.divider()
        
        st.write("\n")
        st.write("\n")

        if st.button("**Search Trains**", type="primary"):
            if st.session_state.boarding_station and st.session_state.destination_station:
                train_schedule_df = Search_Trains(
                    st.session_state.boarding_station_code,
                    st.session_state.destination_station_code,
                    st.session_state.journey_date,
                )

                if not train_schedule_df.empty:
                    for _, row in train_schedule_df.iterrows():
                        with st.container():
                            st.subheader(f"Train {row['train_name']} ({row['train_no']})")
                            col1, col2, col3 = st.columns(3)

                            with col1:
                                st.markdown(f"**Boarding Station:** {st.session_state.boarding_station}")
                                st.markdown(f"**Departure Time:** {row['boarding_departure_time']}")
                                st.markdown(f"**Boarding Date:** {row['boarding_date']}")

                            with col2:
                                st.markdown("<h1 style='text-align: center;'>➔</h1>", unsafe_allow_html=True)

                            with col3:
                                st.markdown(f"**Destination Station:** {st.session_state.destination_station}")
                                st.markdown(f"**Arrival Time:** {row['destination_arrival_time']}")
                                st.markdown(f"**Destination Date:** {row['destination_date']}")

                                if st.button(
                                    "Book Now",
                                    key=f"book_{row['train_no']}",
                                    on_click=start_booking,
                                    args=(row['train_no'], st.session_state.num_tickets),
                                ):
                                    st.write("Button clicked")

                            st.divider()

                else:
                    st.warning("No trains found for the selected route and date.")

            else:
                st.error("Please select both boarding and destination stations.")

    with tabs[1]:
        find_route()
        
    with tabs[2]:
        show_bookings()
        

          
if __name__ == "__main__":
    
    if st.session_state.sess == False :
        auth()
        
    else :
        app()
        