# relationship_steps.py - steps for story 5 (link a todo to a project or category)
#
# Part of the step definition library for the story tests. It holds the steps
# that deal with relationships between todos, projects and categories:
#   - setup (Given): link a todo to a project
#   - actions (When): link, unlink, and the error cases with ids that do not exist
#   - checks (Then): look at the relationship from the todo side and from the
#     project or category side
#
# These steps are also used by story 3 (deleting a todo that is linked to a project).
# Shared steps (status code, API check, creating a project or category) are in
# common_steps.py. Every request goes through helpers.py.

from pytest_bdd import given, when, then, parsers

from helpers import call


# Relationship GETs wrap the list in an object, e.g. {"projects": [...]},
# so this returns just the ids from the list under the given key.
def ids(response, key):
    return [item["id"] for item in response.json().get(key, [])]


# ---------- setup ----------

# Links the scenario's todo to its project before the scenario's When step.
@given("the todo is linked to the project")
def todo_linked(ctx):
    response = call("POST", f"/todos/{ctx['todo_id']}/tasksof", json={"id": ctx["project_id"]})
    assert response.status_code == 201


# ---------- actions ----------

# POST /todos/:id/tasksof
@when("I link the todo to the project")
def link_to_project(ctx):
    ctx["response"] = call("POST", f"/todos/{ctx['todo_id']}/tasksof", json={"id": ctx["project_id"]})


# DELETE /todos/:id/tasksof/:projectid
@when("I unlink the todo from the project")
def unlink_from_project(ctx):
    ctx["response"] = call("DELETE", f"/todos/{ctx['todo_id']}/tasksof/{ctx['project_id']}")


# POST /todos/:id/categories
@when("I link the todo to the category")
def link_to_category(ctx):
    ctx["response"] = call("POST", f"/todos/{ctx['todo_id']}/categories", json={"id": ctx["category_id"]})


# Error case: link to a project id that does not exist (the API answers 404).
@when(parsers.re(r"I link the todo to a project with id (?P<project_id>\d+)"))
def link_to_missing_project(ctx, project_id):
    ctx["response"] = call("POST", f"/todos/{ctx['todo_id']}/tasksof", json={"id": project_id})


# Error case: unlink from a project id that does not exist (the API answers 404).
@when(parsers.re(r"I unlink the todo from a project with id (?P<project_id>\d+)"))
def unlink_from_missing_project(ctx, project_id):
    ctx["response"] = call("DELETE", f"/todos/{ctx['todo_id']}/tasksof/{project_id}")


# BUG-012: unlink using a todo id that does not exist.
# Expected 404, the API answers 400 with a null-pointer style message.
@when(parsers.re(r"I unlink the non-existent todo with id (?P<todo_id>\d+) from the project"))
def unlink_missing_todo(ctx, todo_id):
    ctx["response"] = call("DELETE", f"/todos/{todo_id}/tasksof/{ctx['project_id']}")


# BUG-013: ask for the tasks of a project id that does not exist.
@when(parsers.re(r"I request the tasks of the non-existent project with id (?P<project_id>\d+)"))
def request_tasks_of_missing_project(ctx, project_id):
    ctx["response"] = call("GET", f"/projects/{project_id}/tasks")


# BUG-008 (Part A): ask for the tasksof of a todo id that does not exist.
@when(parsers.re(r"I request the tasksof of the non-existent todo with id (?P<todo_id>\d+)"))
def request_tasksof_of_missing_todo(ctx, todo_id):
    ctx["response"] = call("GET", f"/todos/{todo_id}/tasksof")


# ---------- assertions ----------

# The last response includes the scenario's todo.
@then("the response lists the todo")
def response_lists_todo(ctx):
    assert ctx["todo_id"] in ids(ctx["response"], "todos")


# BUG-013: the API returned a list of todos instead of an error.
# The todos belong to another project, not to the missing one.
@then("the response lists todos instead of an error")
def response_lists_todos_not_error(ctx):
    body = ctx["response"].json()
    assert "errorMessages" not in body
    assert body["todos"] != []


# The last response includes the scenario's project.
@then("the response lists the project")
def response_lists_project(ctx):
    assert ctx["project_id"] in ids(ctx["response"], "projects")


# Todo side of the link: GET /todos/:id/tasksof includes the project.
@then("the todo shows the project in its tasksof relationship")
def todo_side_has_project(ctx):
    response = call("GET", f"/todos/{ctx['todo_id']}/tasksof")
    assert ctx["project_id"] in ids(response, "projects")


# Project side of the link: GET /projects/:id/tasks includes the todo.
@then("the project shows the todo in its tasks relationship")
def project_side_has_todo(ctx):
    response = call("GET", f"/projects/{ctx['project_id']}/tasks")
    assert ctx["todo_id"] in ids(response, "todos")


# After unlinking, the project is gone from the todo side...
@then("the todo no longer shows the project in its tasksof relationship")
def todo_side_lost_project(ctx):
    response = call("GET", f"/todos/{ctx['todo_id']}/tasksof")
    assert ctx["project_id"] not in ids(response, "projects")


# ...and the todo is gone from the project side.
@then("the project no longer shows the todo in its tasks relationship")
def project_side_lost_todo(ctx):
    response = call("GET", f"/projects/{ctx['project_id']}/tasks")
    assert ctx["todo_id"] not in ids(response, "todos")


# After a refused link, the todo has no project at all.
@then("the todo shows no project in its tasksof relationship")
def todo_has_no_project(ctx):
    response = call("GET", f"/todos/{ctx['todo_id']}/tasksof")
    assert ids(response, "projects") == []


# Todo side of the category link: GET /todos/:id/categories includes the category.
@then("the todo shows the category in its categories relationship")
def todo_side_has_category(ctx):
    response = call("GET", f"/todos/{ctx['todo_id']}/categories")
    assert ctx["category_id"] in ids(response, "categories")


# BUG-010: the category side does not show the link (a project link is shown on both sides).
@then("the category does not show the todo in its todos relationship")
def category_side_empty(ctx):
    response = call("GET", f"/categories/{ctx['category_id']}/todos")
    assert ctx["todo_id"] not in ids(response, "todos")


# Used by story 3: deleting a todo must not delete the project it was linked to.
@then("the project still exists")
def project_still_exists(ctx):
    assert call("GET", f"/projects/{ctx['project_id']}").status_code == 200
