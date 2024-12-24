# Ticketing and Transaction Management System (TTMS)

## Overview
This project is a **Ticketing and Transaction Management System (TTMS)** designed for a train reservation platform. It manages user reservations, seat availability, wallet transactions, passenger cancellations, and waitlist updates. It ensures seamless transaction management with rollback and commit operations for database consistency.

---

## Features

1. **Wallet Integration**:
   - Deduction of ticket fare from the user's wallet.
   - Transfer of fare to the IRCTC wallet upon successful booking.
   - Refund handling for cancellations.

2. **Reservation Management**:
   - Seat allocation based on availability.
   - Dynamic handling of passenger reservation statuses (Confirmed/Waitlisted).
   - Real-time database updates for seat availability.

3. **Cancellation Process**:
   - Refund calculation based on cancellation policies (80% refund).
   - Automatic seat reassignment for waitlisted passengers.
   - Updates the database to reflect seat availability upon cancellation.

4. **Database Operations**:
   - Multiple queries for reservations, payments, cancellations, and waitlist management.
   - Use of transactions to ensure atomicity and data consistency.

5. **Passenger Management**:
   - Addition of passengers to the database with details like name, gender, age, and seat status.
   - Dynamic seat and status updates for each passenger.

---

## Technologies Used
- **Python** for backend logic and database interaction.
- **MySQL** for database management.
- **Streamlit** for the user interface and session handling.

---

## Prerequisites
1. **Python 3.x**
2. **MySQL Server**
3. Required Python Libraries:
   - `mysql-connector-python`
   - `streamlit`

---

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/TTMS.git
   cd TTMS
### Install Dependencies
2. To install the required dependencies, use the following command:
   ```bash
    pip install mysql-connector-python streamlit

3.Set up the database with necessary schema and tables.
4.Start the application:

    `streamlit run main.py`

### Database Schema
- Wallet: Stores user balances.
- Reservation: Holds booking details.
- Passenger: Tracks individual passengers and their statuses.
- Payment: Records payment details.
- Availability: Tracks seat availability per train.
- Cancellation: Logs refund details upon cancellations.
### Acknowledgments
   This project was a collaborative effort, and my primary role was to implement the transaction management logic, ensuring robust and consistent operations for reservations and cancellations.

   
---

### Bullet Points for Resume

- **Transaction Management**:
  - Designed and implemented robust database transaction logic for a Ticketing and Transaction Management System (TTMS), ensuring data consistency with rollback and commit operations.
  
- **Database Operations**:
  - Developed and optimized multi-query operations for seat allocation, payment processing, reservation, and cancellations in MySQL.

- **Wallet Integration**:
  - Integrated user wallet functionality, enabling seamless fund transfer, fare deduction, and automated refund processing.

- **Passenger and Seat Management**:
  - Automated passenger status updates (Confirmed/Waitlisted) and dynamic seat allocation/reallocation using MySQL triggers and logic.

- **Cancellations and Refunds**:
  - Implemented real-time refund calculation based on cancellation policies and automated reallocation of seats for waitlisted passengers.

- **Streamlit Application**:
  - Collaborated on building a user-friendly interface with Streamlit for train reservation management.

- **System Reliability**:
  - Ensured atomicity and data integrity across critical operations using transaction handling and exception management.


   
