# Smart Bus Ticket Booking & Reservation System — Project Handoff

## Instructions for the AI coding assistant

You are taking over a beginner-friendly Python project based on the requirements in this document. **Start implementing the project now**, rather than only explaining it or asking broad questions. Work incrementally, keep the code understandable for a beginner, and explain each module briefly as you implement it.

If you have access to a coding workspace or terminal, create and test the files directly. If you only have chat access, provide complete file contents and clear run instructions. Do not claim tests passed unless you actually ran them.

## 1. Project overview

Build a text-based **Smart Bus Ticket Booking & Reservation System** using Python 3. It manages bus routes, searches, ticket bookings, cancellations, seat availability, schedules, and booking reports.

This project is intended to demonstrate beginner Python concepts. Keep the implementation simple, readable, and easy to explain in a viva/presentation.

## 2. Technical constraints

- Language: Python 3.
- Use only Python's built-in functionality; do not install external packages.
- Interface: console/terminal menu.
- Storage: in-memory Python data structures only.
- Do not add a GUI, website, API, payment gateway, external database, or persistence unless explicitly requested later.
- Data is lost when the program exits. Clearly mention this limitation in the README.
- Use descriptive variable/function names, consistent indentation, and helpful comments.
- Safely handle invalid input and numeric conversions.
- Implement features as small functions rather than one enormous block.

## 3. Required project files

Create these files:

1. `main.py` — complete runnable program.
2. `README.md` — purpose, requirements, how to run, menu guide, sample workflow, limitations.
3. `test_cases.txt` — test ID, scenario, input/action, expected result, actual result, pass/fail.
4. `screenshots/` — directory for screenshots of route listing, successful booking, cancellation, and report output, if the environment can capture screenshots. Never invent screenshots; if unavailable, explain how the user can capture them.

## 4. Menu

The supplied Product Requirements Document specifies these options:

1. View Available Routes
2. Search for a Route
3. Book a Ticket
4. View My Bookings
5. Cancel a Booking
6. View Seat Availability
7. Generate Booking Report
8. Exit

The PRD also requires a city-wise Route Schedule feature but does not give it a main-menu number. To make every required feature reachable, add `8. View Route Schedule by Departure City` and move `Exit` to option `9`. Document this small menu adjustment in README. The menu must repeat after each operation until Exit is selected.

Handle non-numeric input and unsupported menu choices without crashing.

## 5. Starter route data

Create five fictional routes with these exact sample values:

| Route ID | Departure city | Destination city | Departure time | Fare (Rs.) | Total seats | Available seats |
|---|---|---|---|---:|---:|---:|
| R101 | Karachi | Hyderabad | 08:00 AM | 1200 | 40 | 40 |
| R102 | Karachi | Sukkur | 09:30 AM | 2000 | 36 | 36 |
| R103 | Hyderabad | Mirpur Khas | 11:00 AM | 800 | 32 | 32 |
| R104 | Karachi | Lahore | 07:00 PM | 5000 | 45 | 45 |
| R105 | Sukkur | Hyderabad | 02:00 PM | 1500 | 30 | 30 |

Represent routes as a list of dictionaries. Each route dictionary must include:
- `route_id`
- `departure_city`
- `destination_city`
- `departure_time`
- `ticket_price`
- `total_seats`
- `available_seats`

Supported cities, in this order:
`("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")`

## 6. Data model

Use beginner-appropriate built-in data structures:

- `routes`: list of route dictionaries.
- `bookings`: list of booking dictionaries, initially empty.
- `cities`: tuple of supported cities.
- `booking_ids`: set of issued booking IDs.
- Each booking record must contain equivalent fields to:
  - `booking_id` (e.g. `B1001`)
  - `passenger_name`
  - `passenger_age`
  - `route_id`
  - `seats`
  - `total_fare`
  - `status` (`"Confirmed"` or `"Cancelled"`)

A booking refers to a route by its `route_id`; this is an in-memory relationship, not a database.

Generate unique booking IDs during the program run. A simple increasing counter starting at `B1001` is fine, provided uniqueness is checked/maintained with the set. Do not reuse an issued ID after cancellation.

## 7. Functional requirements

### Module 1 — Data setup
Initialize route data, supported cities, empty bookings, issued-ID set, and any simple booking counter required.

### Module 2 — Main menu
Display the menu at startup and after each operation. Dispatch each choice to its corresponding function. Exit cleanly.

### Module 3 — View available routes
Display route number, ID, journey, departure time, fare, seats remaining/total, and status.
- Use `for` and `enumerate()` meaningfully.
- If an available-only filter is offered, use `continue` to skip routes with zero available seats.
- Show `Fully Booked` when availability is zero.
- Empty or unusual states should not crash the program.

### Module 4 — Search routes
Search by route ID, departure city, or destination city.
- City matching must be case-insensitive (e.g. use `lower()`).
- A city search should show all matching routes.
- A unique route-ID match may stop the loop with `break`.
- Use `for-else` meaningfully to display a no-match message when no match is found. Ensure the logic still works when a city has multiple matches.

### Module 5 — Book a ticket
Collect passenger name, age, route ID, and seat quantity. Validate all inputs before mutating route/booking state.
- Reject an empty or whitespace-only passenger name.
- Age must be a positive integer; reject text, zero, and negative numbers.
- Route ID must identify an existing route.
- Seat quantity must be a positive integer.
- Reject a request for more seats than are available.
- Generate a unique booking ID.
- Calculate total fare as `ticket_price * seats`.
- Store the booking with `"Confirmed"` status.
- Only after all checks pass, append the booking and decrement route availability.
- Failed requests must not create a confirmed booking or change seat counts.
- Display booking ID, passenger, route/journey, number of seats, fare per seat, total fare, and status after a successful booking.

### Module 6 — View bookings
List all booking records, including cancelled records, with booking ID, passenger, route, seats, total fare, and status.
- Use `for` and `enumerate()` meaningfully.
- If there are no bookings, print `No bookings found.`

### Module 7 — Cancel a booking
- Ask for a booking ID and find the corresponding record.
- If it does not exist, show a helpful message and change nothing.
- Only `"Confirmed"` bookings can be cancelled.
- For a valid cancellation, find the original route, restore exactly the booking's seat quantity once, and change status to `"Cancelled"`.
- Keep the cancelled record in booking history; do not delete it.
- A repeated cancellation must not restore seats again.
- Change status and availability as one logical operation.

### Module 8 — Seat availability
Show available seats versus total capacity for each route.
Classify status as:
- `Available` when all seats remain.
- `Partially Booked` when some seats remain.
- `Fully Booked` when zero seats remain.
Optionally offer a filter for routes with seats remaining.
Maintain `0 <= available_seats <= total_seats`.

### Module 9 — Booking report
Report:
- Total bookings created: count all records, including cancelled.
- Confirmed bookings: count records whose status is `"Confirmed"`.
- Cancelled bookings: count records whose status is `"Cancelled"`.
- Seats currently reserved: sum `seats` from confirmed bookings only.
- Confirmed revenue: sum `total_fare` from confirmed bookings only; exclude cancelled bookings.
- Fully booked routes: count routes with zero available seats.
- Use nested loops to group/inspect confirmed bookings by route, as required by the PRD.
- With no bookings, booking counts, reserved seats, and revenue must be zero; still count full routes correctly.

### Module 10 — Route schedule by departure city
Use an outer loop over `cities` and an inner loop over `routes`. For each city, display routes whose departure city matches that city. If none depart from a city, display `No scheduled departures.` Use nested loops meaningfully.

### Module 11 — Testing and documentation
Include test cases for the scenarios below. Do not fabricate actual test results; mark them `Not run` until executed, then record the actual result.

## 8. Business rules that must never be broken

1. Validate input before changing state.
2. Never allow available seats to become negative or exceed total capacity.
3. Never create a confirmed booking when any validation fails.
4. Never restore seats unless a Confirmed booking is changing to Cancelled.
5. Never restore seats twice for the same booking.
6. Keep cancelled records visible in history.
7. Exclude cancelled bookings from reserved-seat and confirmed-revenue totals.
8. Booking IDs must be unique within a program run.
9. Empty booking lists and invalid inputs are normal cases and must be handled safely.

## 9. Required Python concepts

Use these concepts where appropriate and ensure the code is understandable enough for a beginner to explain them:

- `print()` and `input()`
- variables and basic data types
- strings, integers, floats/integers, booleans
- lists, dictionaries, tuples, sets
- `if`, `elif`, `else`
- nested conditions
- `for`, nested `for` loops, `while`
- `for-else`
- `break`, `continue`
- `enumerate()`
- fare calculation and input validation

Do not force a concept into the code where it makes the logic less clear. Where the PRD explicitly requires a concept, use it meaningfully.

## 10. Required test scenarios

Put these in `test_cases.txt`. Include columns/fields for test ID, scenario, input/action, expected result, actual result, and status. Leave actual result as `Not run` and status as `Not run` until the test has genuinely been executed.

- TC-01: View all five routes and their seat status.
- TC-02: Search `Hyderabad`; show every route departing from or arriving at Hyderabad.
- TC-03: Search an unknown city such as `Atlantis`; show a no-match message and continue.
- TC-04: Book two seats on R101; with valid passenger details, total fare is Rs. 2,400 and availability drops from 40 to 38.
- TC-05: Attempt to book zero seats; reject with no record/seat change.
- TC-06: Request more seats than available; reject without negative availability.
- TC-07: Cancel a confirmed booking; status changes and seats are restored correctly.
- TC-08: Cancel the same booking again; reject and do not restore seats a second time.
- TC-09: Generate report with no bookings; counts, reserved seats, and revenue are zero.
- TC-10: Book exactly all remaining seats; booking succeeds and route becomes Fully Booked.
- TC-11: Generate report after cancellation; cancelled count rises and cancelled fare is excluded.
- TC-12: Enter invalid menu text/number; show a helpful error and return to menu.

## 11. Deliverables and acceptance criteria

The project is complete when:
- At least five routes are shown.
- Search returns all matching routes or a useful no-match message.
- Valid bookings have unique IDs and correct fare.
- Invalid passenger data, route IDs, and seat requests are rejected without changing data.
- Seat counts update correctly after booking and cancellation.
- A booking can only be cancelled once.
- Cancelled bookings remain in history but do not contribute to confirmed revenue.
- Availability never falls outside 0 to total capacity.
- Schedule uses nested loops.
- `enumerate()`, `for-else`, `break`, and `continue` are used meaningfully.
- Empty lists and invalid menu input are handled without crashing.
- README explains how to run the project and that data is not persisted after exit.

## 12. How to work

1. Inspect the current workspace first, if available, so you do not overwrite unrelated files.
2. Implement `main.py` as a complete, runnable program with small, descriptive functions.
3. Run it and test as many required scenarios as the environment permits.
4. Fix bugs found by tests; do not merely report them.
5. Create `README.md` and `test_cases.txt`.
6. Provide concise instructions to run the program, such as `python main.py`.
7. Summarize the functions/modules implemented and clearly report which tests were actually run and which were not.
8. If tools allow direct file editing, do the work in the workspace. Otherwise return the complete contents of the required files.
9. Keep explanations beginner-friendly, preferably in Roman Urdu when explaining to the user.
10. Do not add optional enhancements (discounts, seat numbers, database, GUI, login) until every core requirement is working.

**Begin now by checking the workspace and implementing the project.**
