"""
Tests for the click_step_button tool (Team 03).

Run from the MAIN project folder (not inside team_tests):
    python3 -m team_tests.test_click_step_button

What happens:
  * The TEST (not the tool) uses Playwright to get to each screen:
    it chooses the airports and picks a flight. The tool only clicks.
  * Then the test calls the tool: click_step_button.run(page, argument, context)
  * After every call, the test looks at the REAL page itself, so we do not
    just trust what the tool says about itself.
"""

import sys
import browser_tools
from team_tools import click_step_button

results = []   # list of (test name, passed?)


def record(name, passed):
    """Save and print one PASS/FAIL line."""
    results.append((name, passed))
    if passed:
        print("   PASS:", name)
    else:
        print("   FAIL:", name)


def is_valid(argument):
    """Ask the tool's validate(). It may return True/False or (True/False, reason)."""
    answer = click_step_button.validate(argument)
    if isinstance(answer, tuple):
        return answer[0]
    return answer


# ---------------------------------------------------------------------------
# Part A: argument checks (no browser needed)
# ---------------------------------------------------------------------------
print("=== PART A: validate() rejects bad arguments ===")

argument = {"button": "search_flights"}
print("validate(", argument, ")")
record("validate accepts search_flights", is_valid(argument) is True)

argument = {"button": "confirm_reservation"}
print("validate(", argument, ")")
record("validate REJECTS confirm_reservation", is_valid(argument) is False)

argument = {"button": "launch_rocket"}
print("validate(", argument, ")")
record("validate rejects an unknown button", is_valid(argument) is False)

argument = {}
print("validate(", argument, ")")
record("validate rejects a missing 'button'", is_valid(argument) is False)

# ---------------------------------------------------------------------------
# Part B: browser tests
# ---------------------------------------------------------------------------
browser_tools.start_browser()
try:
    browser_tools.open_site()
    page = browser_tools.page
    context = {}   # this tool does not need trusted context

    # ===== TEST 1: SUCCESS - click Search flights =========================
    print("\n=== TEST 1 (success): search_flights ===")

    # Setup done by the TEST, not the tool: choose From and To.
    page.select_option("#fromAirport", "DCA")
    page.select_option("#toAirport", "BOS")

    call = {"button": "search_flights"}
    print("Tool call:", call)
    result = click_step_button.run(page, call, context)
    print("Tool returned:", result)

    # Independent check: look at the real page ourselves.
    results_visible = page.locator("#resultsStage").is_visible()
    print("Browser evidence: #resultsStage visible =", results_visible)
    print("Browser evidence: URL =", page.url)

    record("search_flights: tool says ok", result["ok"] is True)
    record("search_flights: #resultsStage is really visible", results_visible)

    # ===== TEST 2: FAILURE - Continue before choosing a seat ==============
    print("\n=== TEST 2 (failure): continue_from_seat with NO seat chosen ===")

    # Setup done by the TEST: wait for the flight list (about 1.2 seconds),
    # then choose the first flight so the seat screen appears.
    page.wait_for_selector("button.choose")
    page.locator("button.choose").first.click()
    page.wait_for_selector("#seatStage", state="visible")

    call = {"button": "continue_from_seat"}
    print("Tool call:", call)
    result = click_step_button.run(page, call, context)
    print("Tool returned:", result)

    # Independent check: we must still be on the seat screen.
    seat_visible = page.locator("#seatStage").is_visible()
    passenger_visible = page.locator("#passengerStage").is_visible()
    print("Browser evidence: #seatStage visible =", seat_visible)
    print("Browser evidence: #passengerStage visible =", passenger_visible)

    # The tool should report that it did not click.
    clicked = result["data"].get("clicked")
    print("Tool says clicked =", clicked)

    record("continue_from_seat: tool reports ok = False", result["ok"] is False)
    record("continue_from_seat: tool reports clicked = False", clicked is False)
    record("continue_from_seat: #seatStage is still visible", seat_visible)
    record("continue_from_seat: #passengerStage is still hidden",
           passenger_visible is False)

    # ===== TEST 3: SAFETY - confirm_reservation must be refused ===========
    print("\n=== TEST 3 (safety): confirm_reservation is refused ===")
    call = {"button": "confirm_reservation"}
    print("Tool call:", call)
    result = click_step_button.run(page, call, context)
    print("Tool returned:", result)
    print("Tool says clicked =", result["data"].get("clicked"))

    # Independent check: the page must not have moved to the review screen.
    review_visible = page.locator("#reviewStage").is_visible()
    print("Browser evidence: #reviewStage visible =", review_visible)

    record("confirm_reservation: tool reports ok = False", result["ok"] is False)
    record("confirm_reservation: nothing clicked, still not on review",
           review_visible is False)

finally:
    browser_tools.close_browser()

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n=== SUMMARY ===")
failed = 0
for name, passed in results:
    if passed:
        print("PASS ", name)
    else:
        print("FAIL ", name)
        failed = failed + 1
print(str(len(results) - failed) + " passed, " + str(failed) + " failed")

if failed > 0:
    sys.exit(1)