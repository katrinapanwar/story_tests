# filter_steps.py - steps for story 4 (filter todos by status)
#
# Part of the step definition library for the story tests. It holds the steps
# that only the filter feature uses:
#   - setup (Given): create the todos listed in a table in the feature file
#   - actions (When): call GET /todos with a doneStatus filter, a title filter, or both
#   - checks (Then): which titles are in the results, what they all have in common,
#     and whether the list is empty
#
# Shared steps (status code, API check, cleanup) are in common_steps.py and conftest.py.
# Every request goes through helpers.py.

from pytest_bdd import given, when, then, parsers

from helpers import call, create_todo


# ---------- setup ----------

# Creates every todo in the table from the feature file (title, doneStatus, description)
# and remembers their ids so the scenario cleans them up afterwards.
@given("the following todos exist:")
def todos_exist(ctx, datatable):
    # first row of the table is the header
    header, *rows = datatable
    for row in rows:
        fields = dict(zip(header, row))
        response = create_todo(fields["title"], fields["doneStatus"], fields["description"])
        assert response.status_code == 201
        ctx["todo_ids"].append(response.json()["id"])


# Small helper for the checks below: the titles in the last response.
def titles(ctx):
    return [todo["title"] for todo in ctx["response"].json()["todos"]]


# ---------- actions ----------

# GET /todos?doneStatus=...
@when(parsers.re(r'I filter todos by doneStatus "(?P<done>[^"]*)"$'))
def filter_by_done(ctx, done):
    ctx["response"] = call("GET", "/todos", params={"doneStatus": done})


# GET /todos?doneStatus=...&title=...
@when(parsers.re(r'I filter todos by doneStatus "(?P<done>[^"]*)" and title "(?P<title>[^"]*)"'))
def filter_by_done_and_title(ctx, done, title):
    ctx["response"] = call("GET", "/todos", params={"doneStatus": done, "title": title})


# GET /todos?title=...
@when(parsers.re(r'I filter todos by title "(?P<title>[^"]*)"'))
def filter_by_title(ctx, title):
    ctx["response"] = call("GET", "/todos", params={"title": title})


# ---------- checks ----------

# Every title listed (separated by commas) must be in the results.
@then(parsers.re(r'the filtered results include "(?P<expected>[^"]*)"'))
def results_include(ctx, expected):
    found = titles(ctx)
    for title in expected.split(","):
        assert title in found, f"{title} missing from {found}"


# None of the titles listed (separated by commas) may be in the results.
@then(parsers.re(r'the filtered results do not include "(?P<unexpected>[^"]*)"'))
def results_exclude(ctx, unexpected):
    found = titles(ctx)
    for title in unexpected.split(","):
        assert title not in found, f"{title} should not be in {found}"


# The results contain exactly one todo, with this title.
@then(parsers.re(r'the only filtered todo is "(?P<title>[^"]*)"'))
def only_this_todo(ctx, title):
    assert titles(ctx) == [title]


# Every todo returned has the given doneStatus.
@then(parsers.re(r'every filtered todo has doneStatus "(?P<done>[^"]*)"'))
def every_todo_has_status(ctx, done):
    for todo in ctx["response"].json()["todos"]:
        assert todo["doneStatus"] == done


# The results list is empty. For an invalid doneStatus this is BUG-005
# (the API answers 200 with an empty list instead of 400).
@then("the filtered results are empty")
def results_empty(ctx):
    assert ctx["response"].json()["todos"] == []
