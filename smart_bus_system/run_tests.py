"""Automated checker: runs main.py once per scenario with scripted keyboard input
and checks the printed output.  Usage:  python run_tests.py
TC-01..TC-12 are the required scenarios; EX-01..EX-11 are extra business-rule checks."""
import os
import re
import subprocess
import sys

# main.py sits in the same folder as this script
MAIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")


def run(lines):
    """Feed the given input lines to main.py; return (stdout, return code)."""
    result = subprocess.run([sys.executable, "-I", MAIN], input="\n".join(lines) + "\n",
                            capture_output=True, text=True, timeout=20)
    return result.stdout + result.stderr, result.returncode


def row(out, route_id):
    """Return the seat-availability table row for a route (last one printed)."""
    matches = [l for l in out.splitlines() if l.startswith(route_id + " ") and "->" in l and "Rs." not in l]
    return matches[-1] if matches else ""


def book(name, age, route, seats):
    return ["3", name, str(age), route, str(seats)]


tests = []


def add(test_id, lines, checks):
    tests.append((test_id, lines, checks))


# ---- Required scenarios TC-01 .. TC-12 ----
add("TC-01", ["1", "n", "9"], [
    lambda o: all(r in o for r in ("R101", "R102", "R103", "R104", "R105")),
    lambda o: len(re.findall(r"\s Available$", o, re.M)) == 5,
    lambda o: "40/40" in o and "36/36" in o and "32/32" in o and "45/45" in o and "30/30" in o,
])
add("TC-02", ["2", "Hyderabad", "9"], [
    lambda o: all(r in o for r in ("R101", "R103", "R105")),
    lambda o: "R102" not in o and "R104" not in o,
])
add("TC-03", ["2", "Atlantis", "9"], [
    lambda o: "No match found" in o,
    lambda o: "Goodbye" in o and o.count("Enter your choice") == 2,
])
add("TC-04", book("Ali Khan", 30, "R101", 2) + ["6", "n", "9"], [
    lambda o: "Booking successful" in o and "B1001" in o,
    lambda o: "Rs. 2,400" in o,
    lambda o: row(o, "R101").split()[-5:-3] == ["38", "40"] or "38" in row(o, "R101"),
    lambda o: "Confirmed" in o,
])
add("TC-05", book("Ali Khan", 30, "R101", 0) + ["4", "6", "n", "9"], [
    lambda o: "Booking failed" in o,
    lambda o: "No bookings found." in o,
    lambda o: "40" in row(o, "R101") and "Available" in row(o, "R101"),
])
add("TC-06", book("Ali Khan", 30, "R101", 41) + ["4", "6", "n", "9"], [
    lambda o: "Booking failed" in o and "only 40" in o,
    lambda o: "No bookings found." in o,
    lambda o: "-" not in row(o, "R101").replace("->", "") and "Available" in row(o, "R101"),
])
add("TC-07", book("Ali Khan", 30, "R101", 2) + ["5", "B1001", "4", "6", "n", "9"], [
    lambda o: "Booking B1001 has been cancelled" in o,
    lambda o: "40/40" in o,
    lambda o: "Cancelled" in o,
    lambda o: "Available" in row(o, "R101") and "Partially" not in row(o, "R101"),
])
add("TC-08", book("Ali Khan", 30, "R101", 2) + ["5", "B1001", "5", "B1001", "6", "n", "9"], [
    lambda o: "already Cancelled" in o,
    lambda o: "42" not in o,
    lambda o: row(o, "R101").split()[-3:] == ["40", "40", "Available"],
])
add("TC-09", ["7", "9"], [
    lambda o: re.search(r"Total bookings created\s*: 0", o),
    lambda o: re.search(r"Confirmed bookings\s*: 0", o),
    lambda o: re.search(r"Cancelled bookings\s*: 0", o),
    lambda o: re.search(r"Seats currently reserved\s*: 0", o),
    lambda o: re.search(r"Confirmed revenue\s*: Rs\. 0", o),
    lambda o: re.search(r"Fully booked routes\s*: 0", o),
])
add("TC-10", book("Ali Khan", 30, "R101", 2) + book("Sara Ahmed", 25, "R101", 38) + ["6", "n", "9"], [
    lambda o: o.count("Booking successful") == 2,
    lambda o: "Rs. 45,600" in o,
    lambda o: "Fully Booked" in row(o, "R101") and " 0 " in row(o, "R101"),
])
add("TC-11", book("Ali Khan", 30, "R101", 2) + book("Sara Ahmed", 25, "R102", 1)
    + ["5", "B1001", "7", "9"], [
    lambda o: re.search(r"Total bookings created\s*: 2", o),
    lambda o: re.search(r"Confirmed bookings\s*: 1", o),
    lambda o: re.search(r"Cancelled bookings\s*: 1", o),
    lambda o: re.search(r"Seats currently reserved\s*: 1", o),
    lambda o: re.search(r"Confirmed revenue\s*: Rs\. 2,000", o),
])
add("TC-12", ["abc", "10", "0", "", "-1", "2.5", "9"], [
    lambda o: o.count("Invalid") == 6,
    lambda o: o.count("Enter your choice") == 7,
    lambda o: "Goodbye" in o and "Traceback" not in o,
])

# ---- Extra scenarios (not in the PRD list; added to cover the business rules) ----
add("EX-01", ["3", "   ", "9"], [
    lambda o: "passenger name cannot be empty" in o,
    lambda o: "Traceback" not in o,
])
add("EX-02", ["3", "Ali", "abc", "3", "Ali", "0", "3", "Ali", "-5", "9"], [
    lambda o: o.count("age must be a whole number greater than 0") == 3,
    lambda o: "Traceback" not in o,
])
add("EX-03", ["3", "Ali", "30", "R999", "4", "9"], [
    lambda o: "does not exist" in o,
    lambda o: "No bookings found." in o,
])
add("EX-04", ["3", "Ali", "30", "R101", "abc", "3", "Ali", "30", "R101", "-2", "4", "9"], [
    lambda o: o.count("number of seats must be a whole number greater than 0") == 2,
    lambda o: "No bookings found." in o,
])
add("EX-05", ["5", "B9999", "5", "", "9"], [
    lambda o: o.count("Cancellation failed") == 2,
    lambda o: "Traceback" not in o,
])
add("EX-06", ["4", "9"], [lambda o: "No bookings found." in o])
add("EX-07", ["8", "9"], [
    lambda o: "Karachi:" in o and "Lahore:" in o,
    lambda o: o.count("No scheduled departures.") == 2,  # Mirpur Khas and Lahore
])
add("EX-08", book("Ali Khan", 30, "R101", 2) + ["5", "B1001"] + book("Sara Ahmed", 25, "R101", 1) + ["4", "9"], [
    lambda o: "B1001" in o and "B1002" in o,   # new ID, old ID not reused
    lambda o: o.count("B1001") >= 2 and "Cancelled" in o and "Confirmed" in o,
])
add("EX-09", book("Ali Khan", 30, "R101", 40) + ["1", "y", "6", "y", "9"], [
    lambda o: "Booking successful" in o,
    lambda o: "R101" not in o.split("--- Available Routes ---")[1].split("--- Seat Availability ---")[0],  # continue skipped it
    lambda o: "R101" not in o.split("--- Seat Availability ---")[1],
])
add("EX-10", book("Ali Khan", 30, "R101", 40) + ["3", "Sara", "25", "R101"] + ["7", "9"], [
    lambda o: "is Fully Booked" in o,
    lambda o: re.search(r"Fully booked routes\s*: 1", o),
    lambda o: re.search(r"Confirmed revenue\s*: Rs\. 48,000", o),
])
add("EX-11", ["2", "r102", "2", "KARACHI", "2", "lahore", "9"], [
    lambda o: o.count("R102") >= 2,  # ID search (case-insensitive) + Karachi search
    lambda o: "R104" in o and "R101" in o,
    lambda o: "Traceback" not in o,
])

all_ok = True
for test_id, lines, checks in tests:
    out, code = run(lines)
    results = [bool(c(out)) for c in checks]
    ok = all(results) and code == 0 and "Traceback" not in out
    all_ok &= ok
    print(f"{test_id}: {'PASS' if ok else 'FAIL'}  checks={results} exit={code}")
    if not ok:
        print(out)
print("ALL PASSED" if all_ok else "SOME FAILED")
