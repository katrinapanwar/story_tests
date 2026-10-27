# common_steps.py - steps shared by all five stories
#
# This file is part of the step definition library for the story tests. It holds
# the steps that more than one feature file needs:
#   - setup steps (Given): check the API is up, record the todo count, and create
#     a todo, project or category to work with
#   - shared checks (Then): status code, error message, and the number of todos
#
# Steps that belong to one story only are in todo_steps.py (stories 1-3),
# filter_steps.py (story 4) and relationship_steps.py (story 5).
# Every step reads and writes the scenario's shared state through the "ctx"
# fixture from conftest.py, and every API call goes through helpers.py.

import pytest
import requests
from pytest_bdd import given, then, parsers

from helpers import (call, todo_count, get_todo_fields, error_text,
                     create_todo, create_project, create_category)


# ---------- background / setup steps ----------

# Used by every Background. Fails the scenario if the todo manager is not running.
@given("the API is responsive")
def api_is_responsive():
    try:
        response = call("GET", "/todos")
    except requests.exceptions.ConnectionError:
        pytest.fail("Todo manager is not running on localhost:4567")
    assert response.status_code == 200, "API did not answer GET /todos with 200"


# Saves the current number of todos so a later step can check it went up, down or stayed the same.
@given("I record the current number of todos")
def record_todo_count(ctx):
    ctx["baseline"] = todo_count()


# Creates a todo through the API and remembers its id (for cleanup) and its original fields
# (so the error scenarios can check the todo was not changed).
@given(parsers.re(
    r'a todo exists with title "(?P<title>[^"]*)", doneStatus "(?P<done>[^"]*)" and description "(?P<description>[^"]*)"'))
def todo_exists(ctx, title, done, description):
    response = create_todo(title, done, description)
    assert response.status_code == 201
    ctx["todo_id"] = response.json()["id"]
    ctx["todo_ids"].append(ctx["todo_id"])
    ctx["original"] = get_todo_fields(ctx["todo_id"])


# Creates a project and remembers its id for the scenario and for cleanup.
@given(parsers.re(r'a project exists with title "(?P<title>[^"]*)"'))
def project_exists(ctx, title):
    response = create_project(title)
    assert response.status_code == 201
    ctx["project_id"] = response.json()["id"]
    ctx["project_ids"].append(ctx["project_id"])


# Creates a category and remembers its id for the scenario and for cleanup.
@given(parsers.re(r'a category exists with title "(?P<title>[^"]*)"'))
def category_exists(ctx, title):
    response = create_category(title)
    assert response.status_code == 201
    ctx["category_id"] = response.json()["id"]
    ctx["category_ids"].append(ctx["category_id"])


# ---------- shared assertions ----------

# Checks the status code of the last request, e.g. "the status code 404 is received".
@then(parsers.parse("the status code {code:d} is received"))
def status_code_is(ctx, code):
    actual = ctx["response"].status_code
    assert actual == code, f"expected {code}, got {actual}: {ctx['response'].text}"


# Checks that the API's error message contains the given text.
@then(parsers.re(r'the error message contains "(?P<text>[^"]*)"'))
def error_message_contains(ctx, text):
    assert text in error_text(ctx["response"])


# The next three compare the current todo count with the one saved by "I record the current number of todos".
@then("the number of todos has increased by one")
def count_increased(ctx):
    assert todo_count() == ctx["baseline"] + 1


@then("the number of todos has decreased by one")
def count_decreased(ctx):
    assert todo_count() == ctx["baseline"] - 1


@then("the number of todos is unchanged")
def count_unchanged(ctx):
    assert todo_count() == ctx["baseline"]


# Fetches the todo created in this scenario by id and checks its title.
@then(parsers.re(r'the todo "(?P<title>[^"]*)" exists in the system'))
def todo_exists_in_system(ctx, title):
    todo = get_todo_fields(ctx["todo_id"])
    assert todo is not None, "todo could not be fetched by id"
    assert todo["title"] == title


# Searches the todo list by title and checks nothing comes back.
@then(parsers.re(r'the todo "(?P<title>[^"]*)" does not exist in the system'))
def todo_missing_from_system(title):
    todos = call("GET", "/todos", params={"title": title}).json()["todos"]
    assert todos == []
