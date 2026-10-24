# Smart Bus Ticket Booking & Reservation System

A text-based (console) Python 3 program to manage bus routes, searches, ticket bookings,
cancellations, seat availability, schedules and booking reports. Written for beginners:
simple functions, built-in data structures only, easy to explain in a viva.

> **Last updated:** 24 Oct 2026

---

## 1. PROJECT STATUS (read this first)

**Overall: 9 of 11 steps done. Current stage = Step 10 (screenshots), which only the human can do.**
The program itself is complete and tested; nothing in `main.py` is waiting to be built.

| Step | Work item | Status |
|---:|---|---|
| 1 | Read requirements (`docs/Smart_Bus_Project_Handoff.md`) and inspect workspace | Done |
| 2 | Create folder structure | Done |
| 3 | Modules 1-2: data setup and main menu | Done |
| 4 | Modules 3-4: view routes and search routes | Done |
| 5 | Module 5: book a ticket (all validation) | Done |
| 6 | Modules 6-7: view bookings and cancel booking | Done |
| 7 | Modules 8-10: seat availability, booking report, route schedule | Done |
| 8 | Testing: TC-01..TC-12 plus 11 extra tests, actually executed | Done (23/23 pass) |
| 9 | Documentation: this README and `test_cases.txt` | Done |
| 10 | **Screenshots** (route list, booking, cancellation, report) | **Pending - human must capture** (see `screenshots/HOW_TO_CAPTURE.txt`) |
| 11 | Final manual review and viva/presentation rehearsal | Pending (human) |

### What is done
- Everything in `main.py`: all 10 modules, 9 menu options, all business rules.
- 23 automated scenarios run and passing (`python run_tests.py`); results recorded honestly in `test_cases.txt`.

### What is left to do
1. **Step 10:** take 4 real screenshots into `screenshots/` (the AI environment cannot capture screenshots, and fake ones must never be made).
2. **Step 11:** run `python main.py` by hand once, read the code with the viva notes in section 9, and rehearse.
3. Optional enhancements (discounts, seat numbers, database, GUI, login) are **not** to be added unless the project owner explicitly asks. Core requirements come first and are finished.

---

## 2. Purpose
Demonstrate beginner Python: `print`/`input`, variables, strings/ints/booleans, lists, dictionaries,
tuples, sets, `if/elif/else`, `for`, nested `for`, `while`, `for-else`, `break`, `continue`,
`enumerate()`, fare calculation and input validation.

## 3. Requirements
- Python 3.7 or newer (developed and tested on Python 3.13).
- No external packages. Nothing to install.

## 4. Folder structure

```
smart_bus_system/
├── main.py                  <- the complete program (run this)
├── README.md                <- this file: status, guide, handoff notes
├── test_cases.txt           <- 12 required + 11 extra test cases with real results
├── run_tests.py             <- automated checker that re-runs all 23 tests
├── docs/
│   └── Smart_Bus_Project_Handoff.md   <- the original requirements (source of truth)
└── screenshots/
    └── HOW_TO_CAPTURE.txt   <- instructions; real .png files still to be added (Step 10)
```

## 5. How to run
```
cd smart_bus_system
python main.py          # on some systems: python3 main.py
```
To re-run the automated tests:
```
python run_tests.py     # prints PASS/FAIL per test and "ALL PASSED"
```

## 6. Menu guide

| Option | What it does |
|---:|---|
| 1 | View Available Routes - all routes with seats and status; optional "only routes with seats left" filter |
| 2 | Search for a Route - type a route ID (e.g. `R101`) or a city; case-insensitive; shows all matches |
| 3 | Book a Ticket - asks name, age, route ID, seats; validates everything first |
| 4 | View My Bookings - all bookings, including cancelled ones |
| 5 | Cancel a Booking - by booking ID; only Confirmed bookings; returns the seats once |
| 6 | View Seat Availability - available vs total per route; optional filter |
| 7 | Generate Booking Report - counts, reserved seats, confirmed revenue, fully booked routes |
| 8 | View Route Schedule by Departure City - grouped by city |
| 9 | Exit |

**Menu adjustment (documented on purpose):** the original PRD menu had 8 options and put *Exit* at 8,
but it also required a city-wise Route Schedule feature with no menu number. To make every feature
reachable, the schedule was added as **option 8** and **Exit moved to option 9**.

The menu repeats after every operation until 9 is chosen. Text, blanks and numbers outside 1-9 print
a helpful message instead of crashing.

## 7. Sample workflow
```
Enter your choice: 1        -> n          (see all 5 routes)
Enter your choice: 3        -> Ali Khan, 30, R101, 2
                               Booking B1001 confirmed, total fare Rs. 2,400, R101 now 38/40
Enter your choice: 4        (B1001 shown as Confirmed)
Enter your choice: 5        -> B1001      (cancelled, R101 back to 40/40)
Enter your choice: 4        (B1001 still listed, now Cancelled)
Enter your choice: 7        (report: 1 total, 0 confirmed, 1 cancelled, revenue Rs. 0)
Enter your choice: 9        (exit)
```

## 8. Data model (all in memory, defined at the top of `main.py`)

| Name | Type | Meaning |
|---|---|---|
| `cities` | tuple | `("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")` |
| `routes` | list of dicts | keys: `route_id`, `departure_city`, `destination_city`, `departure_time`, `ticket_price`, `total_seats`, `available_seats` |
| `bookings` | list of dicts | keys: `booking_id`, `passenger_name`, `passenger_age`, `route_id`, `seats`, `total_fare`, `status` (`"Confirmed"` / `"Cancelled"`) |
| `booking_ids` | set | every booking ID ever issued in this run |
| `next_booking_number` | int | counter starting at 1001 (B1001, B1002, ...) |

A booking points to its route through `route_id` (a simple in-memory link, not a database).

Starter routes: R101 Karachi->Hyderabad 08:00 AM Rs.1200 (40 seats), R102 Karachi->Sukkur 09:30 AM Rs.2000 (36),
R103 Hyderabad->Mirpur Khas 11:00 AM Rs.800 (32), R104 Karachi->Lahore 07:00 PM Rs.5000 (45),
R105 Sukkur->Hyderabad 02:00 PM Rs.1500 (30).

### Functions in `main.py`

| Function | Module | Job |
|---|---|---|
| (top of file) | 1 Data setup | creates cities, routes, bookings, booking_ids, counter |
| `read_positive_int(prompt)` | helper | reads a whole number > 0, returns `None` if invalid |
| `find_route_by_id`, `find_booking_by_id` | helper | look up a record (case-insensitive), return `None` if missing |
| `get_seat_status(route)` | helper | `Available` / `Partially Booked` / `Fully Booked` |
| `get_journey_text(route)` | helper | `"Karachi -> Hyderabad"` |
| `generate_booking_id()` | helper | next unique ID, checked against the set |
| `print_route_table_header`, `print_route_row` | helper | shared table printing |
| `show_menu()`, `main()` | 2 Main menu | `while True` loop and dispatch |
| `view_routes()` | 3 | list routes (+ filter) |
| `search_routes()` | 4 | search by route ID or city |
| `book_ticket()` | 5 | validate, then create booking |
| `view_bookings()` | 6 | list all bookings |
| `cancel_booking()` | 7 | cancel once, restore seats |
| `view_seat_availability()` | 8 | seats vs capacity |
| `generate_report()` | 9 | statistics report |
| `view_route_schedule()` | 10 | city-wise schedule |

## 9. Where each Python concept is used (viva notes)

| Concept | Where |
|---|---|
| `print()` / `input()` | everywhere; `input()` always followed by `.strip()` |
| variables, str/int/bool | fares (int), names (str), flags such as `only_available` |
| list | `routes`, `bookings` |
| dictionary | each route and each booking |
| tuple | `cities` (fixed list of supported cities) |
| set | `booking_ids` (no duplicates; checked in `generate_booking_id`) |
| `if / elif / else` | `get_seat_status`, `main()` dispatch, validation |
| nested conditions | `view_routes` / `search_routes` (an `if` inside a loop's `if`) |
| `for` | all list/report functions |
| **nested `for`** | `generate_report` (routes outer, bookings inner) and `view_route_schedule` (cities outer, routes inner) |
| `while` | `main()` menu loop; `generate_booking_id()` uniqueness loop |
| **`enumerate()`** | `view_routes`, `search_routes` (route numbers), `view_bookings` (booking numbers) |
| **`break`** | `search_routes`: stops once a route ID matches (IDs are unique) |
| **`for-else`** | `search_routes`: the `else` runs only if no route ID matched; it then does the city search and prints the no-match message if nothing was found |
| **`continue`** | `view_routes` and `view_seat_availability`: skip fully booked routes in "only available" mode |
| fare calculation | `ticket_price * seats` in `book_ticket` |
| input validation | `read_positive_int`, name/route/seat checks before any change |
| `global` | `generate_booking_id` updates the counter defined outside the function |

## 10. Business rules and how they are enforced

| Rule | How |
|---|---|
| Validate before changing state | `book_ticket` does every check first and `return`s on failure; data changes only at the end |
| Seats never negative or above capacity | booking rejects `seats > available`; cancel checks `available + seats <= total` before changing |
| No confirmed booking if validation fails | early `return` before `bookings.append` |
| Seats restored only for Confirmed -> Cancelled | `cancel_booking` rejects anything not `"Confirmed"` |
| Never restore twice | second cancel sees status `"Cancelled"` and stops (TC-08) |
| Cancelled records stay visible | status changes; record is never deleted |
| Cancelled excluded from revenue/reserved seats | report only adds bookings with status `"Confirmed"` |
| Unique booking IDs | counter + `booking_ids` set; IDs are never reused |
| Empty lists / bad input are normal | "No bookings found.", `None` returns, no crashes; `EOFError`/Ctrl+C exit politely |

## 11. Design decisions (so a future AI does not "fix" them)
- **Search is one box**, not three sub-menus: the text is first tried as a route ID, then as a departure/destination city.
- **Route numbers** (the `No.` column) are the route's position in the full list, so filtered views keep the same numbers.
- **Booking order of checks:** name -> age -> route ID -> route not full -> seats > 0 -> seats <= available. A full route is rejected before seats are asked.
- **Currency** is shown like `Rs. 2,400`.
- The report's per-route table is built with nested loops, and the reserved-seat/revenue totals are summed from it.
- No optional enhancements were added (see section 1).

## 12. Testing
- Required scenarios TC-01..TC-12 and extra scenarios EX-01..EX-11 are in `test_cases.txt` with real results.
- `run_tests.py` feeds scripted input to `main.py` and checks the output. Latest run: **23 passed, 0 failed.**
- During the first run, 4 checks failed because of mistakes in the *test script* (counting a menu heading, wrong column index, wrong input sequence), not in `main.py`; the script was corrected and everything re-run. No change to `main.py` was needed.
- Not tested: real screenshots (cannot be captured by the AI), behaviour on Python older than 3.7.

## 13. Limitations
- **All data is stored in memory only. Everything (bookings, seat changes) is lost when the program exits.**
- Single user, console only: no GUI, website, API, payment, login or database.
- Booking IDs restart at B1001 every time the program starts.
- Seats are counted, not individually numbered.
- Age is only required to be a positive whole number (no upper limit).

## 14. HANDOFF NOTES FOR ANY AI OR PERSON TAKING OVER THIS FOLDER
1. Read section 1 (status) and `docs/Smart_Bus_Project_Handoff.md` (original requirements) first.
2. The code is **finished**. Do not rewrite it. Only change `main.py` if a bug is found, then re-run `python run_tests.py` and update `test_cases.txt`.
3. Never mark a test "Pass" unless it was really executed. Never invent screenshots.
4. Keep it beginner-friendly: built-in Python only, small functions, comments, no new packages.
5. Do not add optional features unless the owner explicitly asks.
6. When explaining to the owner, use simple Roman Urdu where possible.
7. If you change anything, add a line to the change log below and update the status table.

## 15. Change log
| Date | Change |
|---|---|
| 24 Oct 2026 | Project created: folder structure, `main.py` (all modules), `run_tests.py`, `test_cases.txt` (23 tests run, all pass), README with status tracker. Screenshots and final review left pending. |
