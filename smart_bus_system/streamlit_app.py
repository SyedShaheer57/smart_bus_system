"""
Smart Bus Ticket Booking & Reservation System - STREAMLIT GUI VERSION
=====================================================================
Same project, same business rules as main.py, but with a web-style screen
(buttons, forms, tables) instead of a text menu.

How to run:   streamlit run streamlit_app.py

Notes for beginners
* Streamlit re-runs this whole file every time you click something.
  So data that must survive between clicks is kept in st.session_state.
* Data lives in memory only (per browser tab/session). Refreshing the page
  or restarting the server starts again from the 5 starter routes.
"""

import copy

import streamlit as st

# ============================================================
# MODULE 1 - DATA SETUP
# ============================================================

# Tuple of supported cities (fixed, cannot be changed by accident).
CITIES = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

# The five starter routes (list of dictionaries). We copy this list into the
# session so the original always stays untouched.
STARTER_ROUTES = [
    {"route_id": "R101", "departure_city": "Karachi", "destination_city": "Hyderabad",
     "departure_time": "08:00 AM", "ticket_price": 1200, "total_seats": 40, "available_seats": 40},
    {"route_id": "R102", "departure_city": "Karachi", "destination_city": "Sukkur",
     "departure_time": "09:30 AM", "ticket_price": 2000, "total_seats": 36, "available_seats": 36},
    {"route_id": "R103", "departure_city": "Hyderabad", "destination_city": "Mirpur Khas",
     "departure_time": "11:00 AM", "ticket_price": 800, "total_seats": 32, "available_seats": 32},
    {"route_id": "R104", "departure_city": "Karachi", "destination_city": "Lahore",
     "departure_time": "07:00 PM", "ticket_price": 5000, "total_seats": 45, "available_seats": 45},
    {"route_id": "R105", "departure_city": "Sukkur", "destination_city": "Hyderabad",
     "departure_time": "02:00 PM", "ticket_price": 1500, "total_seats": 30, "available_seats": 30},
]

PAGES = (
    "View Available Routes",
    "Search for a Route",
    "Book a Ticket",
    "View My Bookings",
    "Cancel a Booking",
    "View Seat Availability",
    "Generate Booking Report",
    "View Route Schedule by Departure City",
)


def init_state():
    """Create the in-memory data the first time the page opens."""
    if "routes" not in st.session_state:
        st.session_state.routes = copy.deepcopy(STARTER_ROUTES)  # list of dicts
        st.session_state.bookings = []                           # list of dicts
        st.session_state.booking_ids = set()                     # issued IDs
        st.session_state.next_booking_number = 1001              # B1001, B1002, ...


# ============================================================
# HELPER FUNCTIONS (plain logic, no screen code)
# ============================================================

def find_route_by_id(route_id):
    """Return the route dictionary with this ID (case-insensitive) or None."""
    wanted = str(route_id).strip().upper()
    for route in st.session_state.routes:
        if route["route_id"] == wanted:
            return route
    return None


def find_booking_by_id(booking_id):
    """Return the booking dictionary with this ID (case-insensitive) or None."""
    wanted = str(booking_id).strip().upper()
    for booking in st.session_state.bookings:
        if booking["booking_id"] == wanted:
            return booking
    return None


def get_seat_status(route):
    """Return 'Available', 'Partially Booked' or 'Fully Booked'."""
    if route["available_seats"] == 0:
        return "Fully Booked"
    elif route["available_seats"] == route["total_seats"]:
        return "Available"
    else:
        return "Partially Booked"


def get_journey_text(route):
    """Text like 'Karachi -> Hyderabad'."""
    return route["departure_city"] + " -> " + route["destination_city"]


def money(amount):
    """Format a number like 'Rs. 2,400'."""
    return "Rs. " + f"{amount:,}"


def generate_booking_id():
    """Create a booking ID that has never been issued in this session."""
    number = st.session_state.next_booking_number
    new_id = "B" + str(number)
    # Safety check with the set: keep counting up if the ID somehow exists.
    while new_id in st.session_state.booking_ids:
        number += 1
        new_id = "B" + str(number)
    st.session_state.booking_ids.add(new_id)
    st.session_state.next_booking_number = number + 1  # IDs are never reused
    return new_id


def route_table_row(position, route):
    """One route as a dictionary, ready to show in a table."""
    return {
        "No.": position,
        "Route ID": route["route_id"],
        "Journey": get_journey_text(route),
        "Departs": route["departure_time"],
        "Fare": money(route["ticket_price"]),
        "Seats (left/total)": str(route["available_seats"]) + "/" + str(route["total_seats"]),
        "Status": get_seat_status(route),
    }


# ============================================================
# BUSINESS LOGIC FOR BOOKING AND CANCELLING
# (returns (True/False, message[, record]) so the screen code stays simple)
# ============================================================

def try_book_ticket(passenger_name, passenger_age, route_id, seats):
    """Validate EVERYTHING first; change data only if every check passes."""
    passenger_name = str(passenger_name).strip()
    if passenger_name == "":
        return False, "Booking failed: passenger name cannot be empty.", None

    if not isinstance(passenger_age, int) or isinstance(passenger_age, bool) or passenger_age <= 0:
        return False, "Booking failed: age must be a whole number greater than 0.", None

    route = find_route_by_id(route_id)
    if route is None:
        return False, "Booking failed: route '" + str(route_id) + "' does not exist.", None

    if route["available_seats"] == 0:
        return False, "Booking failed: route " + route["route_id"] + " is Fully Booked.", None

    if not isinstance(seats, int) or isinstance(seats, bool) or seats <= 0:
        return False, "Booking failed: number of seats must be a whole number greater than 0.", None

    if seats > route["available_seats"]:
        return (False, "Booking failed: you asked for " + str(seats) + " seat(s) but only "
                + str(route["available_seats"]) + " are available.", None)

    # ---- All checks passed: now (and only now) change the data. ----
    booking = {
        "booking_id": generate_booking_id(),
        "passenger_name": passenger_name,
        "passenger_age": passenger_age,
        "route_id": route["route_id"],
        "seats": seats,
        "total_fare": route["ticket_price"] * seats,
        "status": "Confirmed",
    }
    st.session_state.bookings.append(booking)
    route["available_seats"] -= seats
    return True, "Booking successful!", booking


def try_cancel_booking(booking_id):
    """Cancel a Confirmed booking and give its seats back exactly once."""
    booking = find_booking_by_id(booking_id)
    if booking is None:
        return False, "Cancellation failed: no booking with ID '" + str(booking_id).strip() + "'."

    # Only Confirmed bookings can be cancelled. This also stops a repeated
    # cancellation from returning the seats twice.
    if booking["status"] != "Confirmed":
        return (False, "Cancellation failed: booking " + booking["booking_id"] + " is already "
                + booking["status"] + ". No seats were changed.")

    route = find_route_by_id(booking["route_id"])
    if route is None:
        return False, "Cancellation failed: the route for this booking could not be found."

    restored_seats = route["available_seats"] + booking["seats"]
    if restored_seats > route["total_seats"]:
        return False, "Cancellation failed: this would put the route above its total capacity. Nothing was changed."

    # Seats and status change together, as one logical step.
    route["available_seats"] = restored_seats
    booking["status"] = "Cancelled"
    return (True, "Booking " + booking["booking_id"] + " has been cancelled. "
            + str(booking["seats"]) + " seat(s) returned to route " + route["route_id"]
            + " (now " + str(route["available_seats"]) + "/" + str(route["total_seats"]) + ").")


# ============================================================
# MODULE 3 - VIEW AVAILABLE ROUTES
# ============================================================

def page_view_routes():
    st.header("View Available Routes")
    routes = st.session_state.routes
    if len(routes) == 0:
        st.info("No routes found.")
        return

    only_available = st.checkbox("Show only routes with seats left", key="routes_only_available")

    rows = []
    # enumerate() gives the route number (starting at 1) and the route itself.
    for position, route in enumerate(routes, start=1):
        if only_available and route["available_seats"] == 0:
            continue  # skip fully booked routes
        rows.append(route_table_row(position, route))

    if len(rows) == 0:
        st.info("No routes with seats left.")
    else:
        st.dataframe(rows, hide_index=True)


# ============================================================
# MODULE 4 - SEARCH ROUTES
# ============================================================

def page_search_routes():
    st.header("Search for a Route")
    search_text = st.text_input("Enter a route ID (e.g. R101) or a city name", key="search_text")
    search_text = search_text.strip().lower()
    if search_text == "":
        st.caption("Type something above to search. Search is not case-sensitive.")
        return

    rows = []
    # Step 1: a route ID is unique, so stop (break) as soon as we find it.
    for position, route in enumerate(st.session_state.routes, start=1):
        if route["route_id"].lower() == search_text:
            rows.append(route_table_row(position, route))
            break
    else:
        # for-else: runs ONLY when the loop above ended without break,
        # i.e. no route ID matched. So treat the text as a city name.
        # Many routes can match a city, so here we do not break.
        for position, route in enumerate(st.session_state.routes, start=1):
            if (route["departure_city"].lower() == search_text
                    or route["destination_city"].lower() == search_text):
                rows.append(route_table_row(position, route))

    if len(rows) == 0:
        st.warning("No match found for '" + search_text + "'. Try a route ID like R101 or a city like Karachi.")
    else:
        st.success(str(len(rows)) + " route(s) found.")
        st.dataframe(rows, hide_index=True)


# ============================================================
# MODULE 5 - BOOK A TICKET
# ============================================================

def page_book_ticket():
    st.header("Book a Ticket")
    routes = st.session_state.routes

    # A short list of routes so the user can pick one easily.
    route_choices = []
    for route in routes:
        route_choices.append(route["route_id"] + " | " + get_journey_text(route) + " | "
                             + route["departure_time"] + " | " + money(route["ticket_price"])
                             + " | " + str(route["available_seats"]) + " seats left")

    with st.form("booking_form"):
        passenger_name = st.text_input("Passenger name", key="book_name")
        passenger_age = st.number_input("Passenger age", min_value=0, value=0, step=1, key="book_age",
                                        help="Must be 1 or more.")
        chosen = st.selectbox("Route", route_choices, key="book_route")
        seats = st.number_input("Number of seats", min_value=0, value=1, step=1, key="book_seats",
                                help="Must be 1 or more and not above the seats left.")
        submitted = st.form_submit_button("Book Ticket")

    if submitted:
        route_id = chosen.split(" | ")[0]
        ok, message, booking = try_book_ticket(passenger_name, int(passenger_age), route_id, int(seats))
        if ok:
            route = find_route_by_id(booking["route_id"])
            st.success(message)
            st.table({
                "Booking ID": [booking["booking_id"]],
                "Passenger": [booking["passenger_name"]],
                "Route": [booking["route_id"] + " (" + get_journey_text(route) + ")"],
                "Seats": [booking["seats"]],
                "Fare per seat": [money(route["ticket_price"])],
                "Total fare": [money(booking["total_fare"])],
                "Status": [booking["status"]],
            })
        else:
            st.error(message)


# ============================================================
# MODULE 6 - VIEW BOOKINGS
# ============================================================

def page_view_bookings():
    st.header("View My Bookings")
    bookings = st.session_state.bookings
    if len(bookings) == 0:
        st.info("No bookings found.")
        return

    rows = []
    for number, booking in enumerate(bookings, start=1):
        route = find_route_by_id(booking["route_id"])
        route_text = booking["route_id"]
        if route is not None:
            route_text = booking["route_id"] + " " + get_journey_text(route)
        rows.append({
            "No.": number,
            "Booking ID": booking["booking_id"],
            "Passenger": booking["passenger_name"],
            "Route": route_text,
            "Seats": booking["seats"],
            "Total fare": money(booking["total_fare"]),
            "Status": booking["status"],
        })
    st.dataframe(rows, hide_index=True)


# ============================================================
# MODULE 7 - CANCEL A BOOKING
# ============================================================

def page_cancel_booking():
    st.header("Cancel a Booking")
    with st.form("cancel_form"):
        booking_id = st.text_input("Booking ID (for example B1001)", key="cancel_id")
        submitted = st.form_submit_button("Cancel Booking")

    if submitted:
        ok, message = try_cancel_booking(booking_id)
        if ok:
            st.success(message)
            st.caption("The record stays in your booking history.")
        else:
            st.error(message)


# ============================================================
# MODULE 8 - SEAT AVAILABILITY
# ============================================================

def page_seat_availability():
    st.header("View Seat Availability")
    routes = st.session_state.routes
    if len(routes) == 0:
        st.info("No routes found.")
        return

    only_available = st.checkbox("Show only routes with seats left", key="seats_only_available")

    rows = []
    for route in routes:
        if only_available and route["available_seats"] == 0:
            continue  # skip fully booked routes
        rows.append({
            "Route ID": route["route_id"],
            "Journey": get_journey_text(route),
            "Available": route["available_seats"],
            "Total": route["total_seats"],
            "Status": get_seat_status(route),
        })

    if len(rows) == 0:
        st.info("No routes with seats left.")
        return

    st.dataframe(rows, hide_index=True)

    # Simple bar chart: seats still available for each route.
    chart_data = {}
    for row in rows:
        chart_data[row["Route ID"]] = row["Available"]
    st.caption("Seats still available per route")
    st.bar_chart(chart_data)


# ============================================================
# MODULE 9 - BOOKING REPORT
# ============================================================

def page_booking_report():
    st.header("Generate Booking Report")
    routes = st.session_state.routes
    bookings = st.session_state.bookings

    total_bookings = len(bookings)  # every record, cancelled ones too
    confirmed_count = 0
    cancelled_count = 0
    for booking in bookings:
        if booking["status"] == "Confirmed":
            confirmed_count += 1
        elif booking["status"] == "Cancelled":
            cancelled_count += 1

    # Nested loops: for each route (outer), inspect every booking (inner)
    # and keep only the CONFIRMED ones that belong to that route.
    reserved_seats = 0
    confirmed_revenue = 0
    by_route_rows = []
    for route in routes:
        route_bookings = 0
        route_seats = 0
        route_revenue = 0
        for booking in bookings:
            if booking["route_id"] == route["route_id"] and booking["status"] == "Confirmed":
                route_bookings += 1
                route_seats += booking["seats"]
                route_revenue += booking["total_fare"]
        by_route_rows.append({
            "Route ID": route["route_id"],
            "Journey": get_journey_text(route),
            "Confirmed bookings": route_bookings,
            "Seats reserved": route_seats,
            "Revenue": money(route_revenue),
        })
        reserved_seats += route_seats
        confirmed_revenue += route_revenue

    fully_booked_routes = 0
    for route in routes:
        if route["available_seats"] == 0:
            fully_booked_routes += 1

    row1 = st.columns(3)
    row1[0].metric("Total bookings created", total_bookings)
    row1[1].metric("Confirmed bookings", confirmed_count)
    row1[2].metric("Cancelled bookings", cancelled_count)
    row2 = st.columns(3)
    row2[0].metric("Seats currently reserved", reserved_seats)
    row2[1].metric("Confirmed revenue", money(confirmed_revenue))
    row2[2].metric("Fully booked routes", fully_booked_routes)

    st.subheader("Confirmed bookings by route")
    st.dataframe(by_route_rows, hide_index=True)


# ============================================================
# MODULE 10 - ROUTE SCHEDULE BY DEPARTURE CITY
# ============================================================

def page_route_schedule():
    st.header("View Route Schedule by Departure City")
    for city in CITIES:                          # outer loop: each city
        st.subheader(city)
        rows = []
        for route in st.session_state.routes:    # inner loop: check every route
            if route["departure_city"] == city:
                rows.append({
                    "Departs": route["departure_time"],
                    "Route ID": route["route_id"],
                    "Journey": get_journey_text(route),
                    "Fare": money(route["ticket_price"]),
                })
        if len(rows) == 0:
            st.write("No scheduled departures.")
        else:
            st.dataframe(rows, hide_index=True)


# ============================================================
# MODULE 2 - MAIN MENU (sidebar navigation)
# ============================================================

def main():
    st.set_page_config(page_title="Smart Bus Ticket Booking", page_icon="🚌", layout="wide")
    init_state()

    st.title("🚌 Smart Bus Ticket Booking & Reservation System")
    st.sidebar.title("Menu")
    page = st.sidebar.radio("Choose an option", PAGES, key="menu_choice")
    st.sidebar.caption("Data is kept in memory only. Refreshing the page or restarting "
                       "the app clears all bookings.")

    if page == PAGES[0]:
        page_view_routes()
    elif page == PAGES[1]:
        page_search_routes()
    elif page == PAGES[2]:
        page_book_ticket()
    elif page == PAGES[3]:
        page_view_bookings()
    elif page == PAGES[4]:
        page_cancel_booking()
    elif page == PAGES[5]:
        page_seat_availability()
    elif page == PAGES[6]:
        page_booking_report()
    else:
        page_route_schedule()


main()
