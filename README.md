# ECSE 429 – Part B: Story Tests for the Todo List Manager REST API

**Student:** Katrina Panwar (Group 18, solo), ID 261038323
**Course:** ECSE 429 Software Validation, McGill University, Fall 2026
**System under test:** REST API Todo List Manager (`runTodoManagerRestAPI-1.5.5.jar`), scope: todos

## Repository contents

| Path | Contents |
|---|---|
| `story_tests/` | Gherkin story test suite (pytest-bdd) and its step definitions |
| `README.md` | This file |

## User stories

| # | Story | Feature file |
|---|---|---|
| 1 | As a user, I want to create a todo so that I can track a task. | `01_create_todo.feature` |
| 2 | As a user, I want to update a todo so that it reflects the current state of my task. | `02_update_todo.feature` |
| 3 | As a user, I want to delete a todo so that finished or mistaken tasks disappear. | `03_delete_todo.feature` |
| 4 | As a user, I want to filter my todos so that I can focus on what is done or still open. | `04_filter_todos.feature` |
| 5 | As a user, I want to link a todo to a project so that I can group related tasks. | `05_link_todo_to_project.feature` |

Every story has a Background section and at least one normal, one alternate and one error flow, all written as Scenario Outlines. In total there are 25 scenario outlines, which run as 51 tests.

## Prerequisites

- Java, to run the todo manager
- Python 3.10 or newer
- `runTodoManagerRestAPI-1.5.5.jar` (provided by the course, not included in this repo)

## How to run

1. Start the service in its own terminal and leave it running. It listens on `http://localhost:4567`.

   ```
   java -jar runTodoManagerRestAPI-1.5.5.jar
   ```

2. In a second terminal, install the dependencies (once):

   ```
   cd story_tests
   pip install -r requirements.txt
   ```

3. Run the tests from inside the `story_tests` folder:

   ```
   pytest -v
   ```

### Useful commands

| Goal | Command |
|---|---|
| Run in a random order (default) | `pytest -v` |
| Repeat a specific random order | `pytest -v -p randomly --randomly-seed=12345` |
| Run in file order | `pytest -v -p no:randomly` |
| Run one story | `pytest -v -m story4` |
| Run one kind of flow | `pytest -v -m error` |

The seed of every random run is printed at the top of the output (`Using --randomly-seed=NNNN`).

### When the service is not running

Stop the jar and run `pytest -v`. Every scenario fails with `Todo manager is not running on localhost:4567` (51 failed).

## Structure of the suite

```
story_tests/
├── features/                   Gherkin stories, one file per story
├── step_definitions/
│   ├── common_steps.py         shared steps (API check, status codes, error messages)
│   ├── todo_steps.py           create, amend, replace and delete todos
│   ├── filter_steps.py         filtering and checking filtered results
│   └── relationship_steps.py   linking and unlinking todos, projects and categories
├── helpers.py                  HTTP helper and request builders
├── conftest.py                 loads the steps and cleans up after every scenario
├── test_stories.py             connects each feature file to pytest
├── pytest.ini                  feature folder and marker registration
└── requirements.txt
```

- **Any order:** each scenario creates its own data and deletes it afterwards, so the tests pass in any order.
- **Reusable steps:** the 58 step definitions are shared across all five features.
- **Initial state restored:** a fixture in `conftest.py` removes every todo, project and category a scenario created.

## Known bugs asserted by the tests

Where the API behaves incorrectly, the scenario asserts the actual behavior and says so in its name, so the suite stays runnable and the bug stays documented.

- Bugs from Part A: BUG-001, BUG-005, BUG-008, BUG-010
- New bugs found in Part B (reports in `bug_reports/`):
  - `Story5_ErrorFlow_Bug_Unlink_NonExistent_Todo`: unlinking a non-existent todo returns 400 instead of 404
  - `Story5_ErrorFlow_Bug_Tasks_Of_NonExistent_Project`: requesting the tasks of a non-existent project returns 200 with unrelated todos instead of 404

## Notes

- The tests expect the service to start from its initial data. Restart the jar if an earlier session left extra data behind.
