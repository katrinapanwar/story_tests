# helpers.py - small functions for talking to the todo manager API
#
# Every step definition uses these helpers instead of building requests itself,
# so the base URL, headers and timeout are defined in one place. Nothing here
# knows about Gherkin or pytest: these are plain functions that send a request
# or read a response.

import requests

BASE_URL = "http://localhost:4567"
JSON = {"Content-Type": "application/json", "Accept": "application/json"}
XML = {"Content-Type": "application/xml", "Accept": "application/json"}


# Sends one request to the API and returns the response. Uses JSON headers unless
# the caller passes others (for example XML), and gives up after 10 seconds.
def call(method, path, **kwargs):
    headers = kwargs.pop("headers", JSON)
    return requests.request(method, BASE_URL + path, headers=headers, timeout=10, **kwargs)


# Feature files carry "true"/"false" as text, but the API needs real booleans.
def to_bool(text):
    return text.strip().lower() == "true"


# Number of todos currently in the system (GET /todos).
def todo_count():
    return len(call("GET", "/todos").json()["todos"])


# Returns the fields of one todo as a dictionary, or None if it does not exist.
# GET /todos/:id wraps the todo in a list, so this unwraps it.
def get_todo_fields(todo_id):
    response = call("GET", f"/todos/{todo_id}")
    if response.status_code != 200:
        return None
    return response.json()["todos"][0]


# The API's error message as one string, or the raw body if it is not JSON.
def error_text(response):
    try:
        return " ".join(response.json().get("errorMessages", []))
    except ValueError:
        return response.text


# Creates a todo (POST /todos) with a title, doneStatus and description.
def create_todo(title, done="false", description=""):
    body = {"title": title, "doneStatus": to_bool(done), "description": description}
    return call("POST", "/todos", json=body)


# Creates a project (POST /projects).
def create_project(title):
    return call("POST", "/projects", json={"title": title})


# Creates a category (POST /categories).
def create_category(title):
    return call("POST", "/categories", json={"title": title})
