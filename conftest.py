# conftest.py - shared setup for the story tests
#
# pytest reads this file automatically before running any test. It does two jobs:
#   1. loads the step definition files, so every feature file can use every step
#   2. provides the "ctx" fixture: the scratch space each scenario uses to share
#      data between its steps, and the cleanup that restores the system afterwards
#
# The check that the todo manager is running is the Background step
# "the API is responsive" in common_steps.py, so every scenario fails if it is down.

import pytest
import requests

from helpers import call

# The step definition files, loaded as plugins so every feature can use them.
pytest_plugins = [
    "step_definitions.common_steps",
    "step_definitions.todo_steps",
    "step_definitions.filter_steps",
    "step_definitions.relationship_steps",
]


# A fresh "ctx" is created for every scenario. Steps use it to remember the last
# response, the ids they created, and the todo count. After the scenario ends
# (pass or fail) everything it created is deleted, so scenarios do not depend on
# each other and can run in any order.
@pytest.fixture
def ctx():
    state = {"todo_ids": [], "project_ids": [], "category_ids": []}
    yield state

    # cleanup: delete every todo, project and category this scenario created
    # if the service is down the Background step already failed the scenario
    try:
        for todo_id in state["todo_ids"]:
            call("DELETE", f"/todos/{todo_id}")
        for project_id in state["project_ids"]:
            call("DELETE", f"/projects/{project_id}")
        for category_id in state["category_ids"]:
            call("DELETE", f"/categories/{category_id}")
    except requests.exceptions.ConnectionError:
        pass
