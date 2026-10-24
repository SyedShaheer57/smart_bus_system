"""
Smart Bus Ticket Booking & Reservation System
=============================================
A text-based (console) program written for beginners.

* Uses only built-in Python features (no external packages).
* All data lives in memory, so everything is lost when the program exits.

How to run:   python main.py
"""

# ============================================================
# MODULE 1 - DATA SETUP
# ============================================================

# A tuple: supported cities (a tuple cannot be changed by accident).
cities = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")

# A list of dictionaries: one dictionary per bus route.
routes = [
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

# A list of dictionaries: every booking ever made (starts empty).
bookings = []

# A set: every booking ID that has been issued (a set never holds duplicates).
booking_ids = set()

# A simple counter: the next booking number to try (B1001, B1002, ...).
next_booking_number = 1001


# ============================================================
# SMALL HELPER FUNCTIONS (used by many modules)
# ============================================================

def read_positive_int(prompt):
    """Ask the user for a whole number greater than 0.

    Returns the number, or None if the input is text, empty, negative,
    decimal or zero. (Returning None instead of crashing keeps us safe.)
    """
    text = input(prompt).strip()
    # isascii() + isdigit() accepts only the characters 0-9, so "abc", "-5",
    # "2.5" and "" are all rejected before we try int().
    if not (text.isascii() and text.isdigit()):
        return None
    number = int(text)
    if number <= 0:
        return None
    return number


def find_route_by_id(route_id):
    """Return the route dictionary with this ID, or None if not found."""
    wanted = route_id.strip().upper()
    for route in routes:
        if route["route_id"] == wanted:
            return route
    return None


def find_booking_by_id(booking_id):
    """Return the booking dictionary with this ID, or None if not found."""
    wanted = booking_id.strip().upper()
    for booking in bookings:
        if booking["booking_id"] == wanted:
            return booking
    return None


def get_seat_status(route):
    """Return 'Available', 'Partially Booked' or 'Fully Booked' for a route."""
    if route["available_seats"] == 0:
        return "Fully Booked"
    elif route["available_seats"] == route["total_seats"]:
        return "Available"
    else:
        return "Partially Booked"


def get_journey_text(route):
    """Return text like 'Karachi -> Hyderabad'."""
    return route["departure_city"] + " -> " + route["destination_city"]


def generate_booking_id():
    """Create a new booking ID that has never been used in this run."""
    global next_booking_number  # we change the counter that lives outside the function
    new_id = "B" + str(next_booking_number)
    # Safety check with the set: keep counting up if the ID somehow exists.
    while new_id in booking_ids:
        next_booking_number += 1
        new_id = "B" + str(next_booking_number)
    booking_ids.add(new_id)
    next_booking_number += 1  # IDs are never reused, even after a cancellation
    return new_id


def print_route_table_header():
    """Print the column titles used when showing routes."""
    print(f"{'No.':<4}{'ID':<6}{'Journey':<26}{'Departs':<10}{'Fare':>10}  {'Seats':<8}Status")
    print("-" * 78)


def print_route_row(position, route):
    """Print one route as one table row."""
    fare_text = "Rs. " + f"{route['ticket_price']:,}"
    seats_text = f"{route['available_seats']}/{route['total_seats']}"
    print(f"{position:<4}{route['route_id']:<6}{get_journey_text(route):<26}"
          f"{route['departure_time']:<10}{fare_text:>10}  {seats_text:<8}{get_seat_status(route)}")


# ============================================================
# MODULE 3 - VIEW AVAILABLE ROUTES
# ============================================================

def view_routes():
    """Show all routes, or only routes that still have seats."""
    print("\n--- Available Routes ---")
    if len(routes) == 0:
        print("No routes found.")
        return

    only_available = input("Show only routes with seats left? (y/n): ").strip().lower()
    print()
    print_route_table_header()

    shown_count = 0
    # enumerate() gives us the route number (starting at 1) and the route itself.
    for position, route in enumerate(routes, start=1):
        if only_available == "y" and route["available_seats"] == 0:
            continue  # skip fully booked routes and jump to the next route
        print_route_row(position, route)
        shown_count += 1

    if shown_count == 0:
        print("No routes with seats left.")


# ============================================================
# MODULE 4 - SEARCH ROUTES
# ============================================================

def search_routes():
    """Search by route ID, departure city or destination city."""
    print("\n--- Search for a Route ---")
    search_text = input("Enter a route ID or a city name: ").strip().lower()
    if search_text == "":
        print("Search text cannot be empty.")
        return

    print()
    # Step 1: a route ID is unique, so stop (break) as soon as we find it.
    for position, route in enumerate(routes, start=1):
        if route["route_id"].lower() == search_text:
            print_route_table_header()
            print_route_row(position, route)
            break
    else:
        # for-else: this "else" runs ONLY when the loop above finished
        # without hitting break, i.e. no route ID matched.
        # Step 2: so treat the text as a city name. Many routes can match,
        # so we do not break here; we keep going and count the matches.
        match_count = 0
        for position, route in enumerate(routes, start=1):
            if (route["departure_city"].lower() == search_text
                    or route["destination_city"].lower() == search_text):
                if match_count == 0:
                    print_route_table_header()  # print the header once, before the first match
                print_route_row(position, route)
                match_count += 1
        if match_count == 0:
            print("No match found for '" + search_text + "'. Try a route ID like R101 or a city like Karachi.")


# ============================================================
# MODULE 5 - BOOK A TICKET
# ============================================================

def book_ticket():
    """Collect and validate passenger details, then create a booking.

    Every check happens BEFORE any data is changed. If a check fails we
    print a message and return, so nothing is booked and no seats change.
    """
    print("\n--- Book a Ticket ---")

    # Check 1: name must not be empty or only spaces.
    passenger_name = input("Passenger name: ").strip()
    if passenger_name == "":
        print("Booking failed: passenger name cannot be empty.")
        return

    # Check 2: age must be a positive whole number.
    passenger_age = read_positive_int("Passenger age: ")
    if passenger_age is None:
        print("Booking failed: age must be a whole number greater than 0.")
        return

    # Check 3: the route must exist.
    route_id = input("Route ID (for example R101): ").strip()
    route = find_route_by_id(route_id)
    if route is None:
        print("Booking failed: route '" + route_id + "' does not exist. Use option 1 to see route IDs.")
        return

    # Check 4: the route must still have seats.
    if route["available_seats"] == 0:
        print("Booking failed: route " + route["route_id"] + " is Fully Booked.")
        return

    print("Route " + route["route_id"] + " (" + get_journey_text(route) + ") has "
          + str(route["available_seats"]) + " seat(s) available.")

    # Check 5: seat quantity must be a positive whole number.
    seats = read_positive_int("Number of seats: ")
    if seats is None:
        print("Booking failed: number of seats must be a whole number greater than 0.")
        return

    # Check 6: cannot book more seats than are available.
    if seats > route["available_seats"]:
        print("Booking failed: you asked for " + str(seats) + " seat(s) but only "
              + str(route["available_seats"]) + " are available.")
        return

    # ---- All checks passed: now (and only now) change the data. ----
    booking_id = generate_booking_id()
    total_fare = route["ticket_price"] * seats

    booking = {
        "booking_id": booking_id,
        "passenger_name": passenger_name,
        "passenger_age": passenger_age,
        "route_id": route["route_id"],
        "seats": seats,
        "total_fare": total_fare,
        "status": "Confirmed",
    }
    bookings.append(booking)
    route["available_seats"] -= seats

    print("\nBooking successful!")
    print("  Booking ID    :", booking_id)
    print("  Passenger     :", passenger_name)
    print("  Route         :", route["route_id"], "(" + get_journey_text(route) + ")")
    print("  Seats booked  :", seats)
    print("  Fare per seat : Rs.", f"{route['ticket_price']:,}")
    print("  Total fare    : Rs.", f"{total_fare:,}")
    print("  Status        :", booking["status"])


# ============================================================
# MODULE 6 - VIEW BOOKINGS
# ============================================================

def view_bookings():
    """List every booking, including cancelled ones."""
    print("\n--- My Bookings ---")
    if len(bookings) == 0:
        print("No bookings found.")
        return

    print(f"{'No.':<4}{'Booking':<8}{'Passenger':<20}{'Route':<30}{'Seats':>5}{'Total Fare':>14}  Status")
    print("-" * 92)
    for number, booking in enumerate(bookings, start=1):
        route = find_route_by_id(booking["route_id"])
        if route is not None:
            route_text = booking["route_id"] + " " + get_journey_text(route)
        else:
            route_text = booking["route_id"]  # should never happen, but stay safe
        fare_text = "Rs. " + f"{booking['total_fare']:,}"
        print(f"{number:<4}{booking['booking_id']:<8}{booking['passenger_name']:<20}"
              f"{route_text:<30}{booking['seats']:>5}{fare_text:>14}  {booking['status']}")


# ============================================================
# MODULE 7 - CANCEL A BOOKING
# ============================================================

def cancel_booking():
    """Cancel a Confirmed booking and give its seats back (exactly once)."""
    print("\n--- Cancel a Booking ---")
    booking_id = input("Enter booking ID (for example B1001): ").strip()
    booking = find_booking_by_id(booking_id)

    if booking is None:
        print("Cancellation failed: no booking with ID '" + booking_id + "'. Use option 4 to see your bookings.")
        return

    # Only Confirmed bookings can be cancelled. This one check also stops a
    # second cancellation from giving the seats back twice.
    if booking["status"] != "Confirmed":
        print("Cancellation failed: booking " + booking["booking_id"] + " is already "
              + booking["status"] + ". No seats were changed.")
        return

    route = find_route_by_id(booking["route_id"])
    if route is None:
        print("Cancellation failed: the route for this booking could not be found.")
        return

    # Work out the new seat count first, and make sure it is legal.
    restored_seats = route["available_seats"] + booking["seats"]
    if restored_seats > route["total_seats"]:
        print("Cancellation failed: this would put the route above its total capacity. Nothing was changed.")
        return

    # Seats and status change together, as one logical step.
    route["available_seats"] = restored_seats
    booking["status"] = "Cancelled"

    print("\nBooking " + booking["booking_id"] + " has been cancelled.")
    print("  Seats returned to route " + route["route_id"] + ": " + str(booking["seats"]))
    print("  Seats now available      : " + str(route["available_seats"]) + "/" + str(route["total_seats"]))
    print("  The record stays in your booking history.")


# ============================================================
# MODULE 8 - SEAT AVAILABILITY
# ============================================================

def view_seat_availability():
    """Show seats left versus total seats for each route."""
    print("\n--- Seat Availability ---")
    if len(routes) == 0:
        print("No routes found.")
        return

    only_available = input("Show only routes with seats left? (y/n): ").strip().lower()
    print()
    print(f"{'ID':<6}{'Journey':<26}{'Available':>10}{'Total':>8}  Status")
    print("-" * 64)

    shown_count = 0
    for route in routes:
        if only_available == "y" and route["available_seats"] == 0:
            continue  # skip fully booked routes
        print(f"{route['route_id']:<6}{get_journey_text(route):<26}"
              f"{route['available_seats']:>10}{route['total_seats']:>8}  {get_seat_status(route)}")
        shown_count += 1

    if shown_count == 0:
        print("No routes with seats left.")


# ============================================================
# MODULE 9 - BOOKING REPORT
# ============================================================

def generate_report():
    """Print booking counts, reserved seats, confirmed revenue and full routes."""
    print("\n--- Booking Report ---")

    total_bookings = len(bookings)      # every record, cancelled ones too
    confirmed_count = 0
    cancelled_count = 0
    for booking in bookings:
        if booking["status"] == "Confirmed":
            confirmed_count += 1
        elif booking["status"] == "Cancelled":
            cancelled_count += 1

    # Nested loops: for each route (outer), look at every booking (inner)
    # and keep only the CONFIRMED ones that belong to that route.
    reserved_seats = 0
    confirmed_revenue = 0
    print("Confirmed bookings by route:")
    for route in routes:
        route_bookings = 0
        route_seats = 0
        route_revenue = 0
        for booking in bookings:
            if booking["route_id"] == route["route_id"] and booking["status"] == "Confirmed":
                route_bookings += 1
                route_seats += booking["seats"]
                route_revenue += booking["total_fare"]
        print(f"  {route['route_id']} {get_journey_text(route):<24} "
              f"bookings: {route_bookings}, seats: {route_seats}, revenue: Rs. {route_revenue:,}")
        reserved_seats += route_seats
        confirmed_revenue += route_revenue

    fully_booked_routes = 0
    for route in routes:
        if route["available_seats"] == 0:
            fully_booked_routes += 1

    print("\nSummary")
    print("  Total bookings created   :", total_bookings)
    print("  Confirmed bookings       :", confirmed_count)
    print("  Cancelled bookings       :", cancelled_count)
    print("  Seats currently reserved :", reserved_seats)
    print("  Confirmed revenue        : Rs.", f"{confirmed_revenue:,}")
    print("  Fully booked routes      :", fully_booked_routes)


# ============================================================
# MODULE 10 - ROUTE SCHEDULE BY DEPARTURE CITY
# ============================================================

def view_route_schedule():
    """Show the departures of every city using nested loops."""
    print("\n--- Route Schedule by Departure City ---")
    for city in cities:                      # outer loop: each city
        print("\n" + city + ":")
        departures_found = 0
        for route in routes:                 # inner loop: check every route
            if route["departure_city"] == city:
                print("  " + route["departure_time"] + "  " + route["route_id"] + "  "
                      + get_journey_text(route) + "  (Rs. " + f"{route['ticket_price']:,}" + ")")
                departures_found += 1
        if departures_found == 0:
            print("  No scheduled departures.")


# ============================================================
# MODULE 2 - MAIN MENU
# ============================================================

def show_menu():
    """Print the main menu."""
    print("\n=========================================")
    print("   SMART BUS TICKET BOOKING SYSTEM")
    print("=========================================")
    print("1. View Available Routes")
    print("2. Search for a Route")
    print("3. Book a Ticket")
    print("4. View My Bookings")
    print("5. Cancel a Booking")
    print("6. View Seat Availability")
    print("7. Generate Booking Report")
    print("8. View Route Schedule by Departure City")
    print("9. Exit")


def main():
    """Show the menu again and again until the user chooses Exit (9)."""
    print("Welcome! (Note: all data is lost when you exit.)")

    while True:
        show_menu()
        choice_text = input("Enter your choice (1-9): ").strip()

        # Handle text such as "abc", "", "-1" or "2.5" without crashing.
        if not (choice_text.isascii() and choice_text.isdigit()):
            print("Invalid input: please type a number from 1 to 9.")
            continue

        choice = int(choice_text)
        if choice == 1:
            view_routes()
        elif choice == 2:
            search_routes()
        elif choice == 3:
            book_ticket()
        elif choice == 4:
            view_bookings()
        elif choice == 5:
            cancel_booking()
        elif choice == 6:
            view_seat_availability()
        elif choice == 7:
            generate_report()
        elif choice == 8:
            view_route_schedule()
        elif choice == 9:
            print("Thank you for using the Smart Bus system. Goodbye!")
            break
        else:
            print("Invalid choice: please pick a number from 1 to 9.")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        # Input ended (Ctrl+D / Ctrl+C / piped input finished): exit politely.
        print("\nProgram ended. Goodbye!")
