# test_stories.py - turns the feature files into pytest tests
#
# Each scenarios(...) line makes pytest read one feature file and create one test
# per scenario, and one per row of each Examples table. The steps those tests run
# are in the step_definitions folder, and the shared setup is in conftest.py.

from pytest_bdd import scenarios

# One call per feature file, so each story's scenarios become normal pytest tests.
scenarios("01_create_todo.feature")   # story 1: create a todo
scenarios("02_update_todo.feature")   # story 2: update a todo
scenarios("03_delete_todo.feature")   # story 3: delete a todo
scenarios("04_filter_todos.feature")  # story 4: filter todos by status
scenarios("05_link_todo_to_project.feature")  # story 5: link a todo to a project