# todo_steps.py - steps for stories 1, 2 and 3 (create, update and delete a todo)
#
# Part of the step definition library for the story tests. It holds the steps
# that deal with a single todo:
#   - story 1 (create): create a todo in different ways, then check what was stored
#   - story 2 (update): amend with POST, replace with PUT, and the error cases
#   - story 3 (delete): delete a todo and check it is gone
#
# Shared steps (status code, API check, todo count, cleanup) are in common_steps.py
# and conftest.py. Every request goes through helpers.py.

from pytest_bdd import given, when, then, parsers

from helpers import call, to_bool, get_todo_fields, XML, create_todo


# Remembers the id of a todo the API just created, so the scenario cleans it up.
# Nothing is remembered when the creation failed (for example an empty title).
def remember_created(ctx, response):
    if response.status_code == 201:
        ctx["todo_id"] = response.json()["id"]
        ctx["todo_ids"].append(ctx["todo_id"])


# ---------- story 1: create ----------

# Normal flow: POST /todos with only a title.
@when(parsers.re(r'I create a todo with title "(?P<title>[^"]*)"$'))
def create_with_title(ctx, title):
    ctx["response"] = call("POST", "/todos", json={"title": title})
    remember_created(ctx, ctx["response"])


# Alternate flow: POST /todos with title, doneStatus and description.
@when(parsers.re(
    r'I create a todo titled "(?P<title>[^"]*)" with doneStatus "(?P<done>[^"]*)" and description "(?P<description>[^"]*)"'))
def create_with_all_fields(ctx, title, done, description):
    ctx["response"] = create_todo(title, done, description)
    remember_created(ctx, ctx["response"])


# Alternate flow: POST /todos with an XML body instead of JSON.
@when(parsers.re(r'I create a todo with title "(?P<title>[^"]*)" using XML'))
def create_with_xml(ctx, title):
    body = f"<todo><title>{title}</title></todo>"
    ctx["response"] = call("POST", "/todos", data=body, headers=XML)
    remember_created(ctx, ctx["response"])


# Error flow: the title is an empty string (the API answers 400).
@when(parsers.re(r'I try to create a todo with an empty title and description "(?P<description>[^"]*)"'))
def create_with_empty_title(ctx, description):
    ctx["response"] = call("POST", "/todos", json={"title": "", "description": description})
    remember_created(ctx, ctx["response"])


# Error flow: the title field is missing (the API answers 400).
@when(parsers.re(r'I try to create a todo with no title and description "(?P<description>[^"]*)"'))
def create_with_no_title(ctx, description):
    ctx["response"] = call("POST", "/todos", json={"description": description})
    remember_created(ctx, ctx["response"])


# A todo created with only a title gets doneStatus "false" and an empty description.
@then(parsers.re(r'the todo "(?P<title>[^"]*)" has default doneStatus and description'))
def has_defaults(ctx, title):
    todo = get_todo_fields(ctx["todo_id"])
    assert todo["doneStatus"] == "false"
    assert todo["description"] == ""


# Fetches the created todo again and checks every field was stored as sent.
@then(parsers.re(
    r'the todo "(?P<title>[^"]*)" is stored with doneStatus "(?P<done>[^"]*)" and description "(?P<description>[^"]*)"'))
def stored_with_fields(ctx, title, done, description):
    todo = get_todo_fields(ctx["todo_id"])
    assert todo["title"] == title
    assert todo["doneStatus"] == done
    assert todo["description"] == description


# ---------- story 2: update ----------

# POST /todos/:id (amend) with only doneStatus; the other fields must stay as they are.
# Also used as a Given in story 3 to set the todo's status before deleting it.
# true/false are sent as real booleans; any other value is sent as text on purpose
# to test the error case (the API answers 400).
@given(parsers.re(r'the todo has doneStatus "(?P<done>[^"]*)"'))
@when(parsers.re(r'I amend the todo setting doneStatus to "(?P<done>[^"]*)"'))
def amend_done_status(ctx, done):
    value = to_bool(done) if done.lower() in ("true", "false") else done
    ctx["response"] = call("POST", f"/todos/{ctx['todo_id']}", json={"doneStatus": value})


# PUT /todos/:id with all fields: the todo is replaced completely.
@when(parsers.re(
    r'I replace the todo with title "(?P<title>[^"]*)", doneStatus "(?P<done>[^"]*)" and description "(?P<description>[^"]*)"'))
def replace_todo(ctx, title, done, description):
    body = {"title": title, "doneStatus": to_bool(done), "description": description}
    ctx["response"] = call("PUT", f"/todos/{ctx['todo_id']}", json=body)


# PUT /todos/:id with only a title: the omitted fields are reset to their defaults.
@when(parsers.re(r'I replace the todo with only the title "(?P<title>[^"]*)"'))
def replace_with_title_only(ctx, title):
    ctx["response"] = call("PUT", f"/todos/{ctx['todo_id']}", json={"title": title})


# Error flow: amend a todo id that does not exist (the API answers 404).
@when(parsers.re(r'I amend the non-existent todo with id (?P<todo_id>\d+) setting title to "(?P<title>[^"]*)"'))
def amend_missing_todo(ctx, todo_id, title):
    ctx["response"] = call("POST", f"/todos/{todo_id}", json={"title": title})


# Fetches the todo again and checks all three fields after an update.
@then(parsers.re(
    r'the todo is stored with title "(?P<title>[^"]*)", doneStatus "(?P<done>[^"]*)" and description "(?P<description>[^"]*)"'))
def todo_stored_with(ctx, title, done, description):
    todo = get_todo_fields(ctx["todo_id"])
    assert todo["title"] == title
    assert todo["doneStatus"] == done
    assert todo["description"] == description


# After a refused update, the todo still has the fields saved when it was created.
@then("the original todo is unchanged")
def original_unchanged(ctx):
    todo = get_todo_fields(ctx["todo_id"])
    for field in ("title", "doneStatus", "description"):
        assert todo[field] == ctx["original"][field]


# ---------- story 3: delete ----------

# Deletes the todo as part of the setup, so the scenario can delete it a second time.
@given("I have already deleted the todo")
def already_deleted(ctx):
    assert call("DELETE", f"/todos/{ctx['todo_id']}").status_code == 200


# DELETE /todos/:id
@when("I delete the todo")
def delete_todo(ctx):
    ctx["response"] = call("DELETE", f"/todos/{ctx['todo_id']}")


# GET /todos/:id again, to confirm what happened (404 once the todo is gone).
@then(parsers.parse("fetching the todo returns status code {code:d}"))
def fetching_returns(ctx, code):
    assert call("GET", f"/todos/{ctx['todo_id']}").status_code == code