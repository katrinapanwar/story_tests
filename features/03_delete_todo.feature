# Story 3 - Delete a todo (DELETE /todos/:id)
# Normal flow:     delete a todo, then it can no longer be fetched
# Alternate flows: delete a todo that is linked to a project, project remains
# Error flows:     delete an id that was already deleted

Feature: Delete a todo
  As a user, I want to delete a todo so that finished or mistaken tasks disappear

  Background:
    Given the API is responsive
    And a todo exists with title "Delete me", doneStatus "false" and description "Temporary"
    And I record the current number of todos

  # Normal Flow
  @story3 @normal
  Scenario Outline: Successfully delete a todo whatever its doneStatus
    Given the todo has doneStatus "<done>"
    When I delete the todo
    Then the status code 200 is received
    And fetching the todo returns status code 404
    And the todo "Delete me" does not exist in the system
    And the number of todos has decreased by one

    Examples:
      | done  |
      | false |
      | true  |

  # Alternate Flow
  @story3 @alternate
  Scenario Outline: Deleting a todo linked to a project keeps the project
    Given a project exists with title "<project>"
    And the todo is linked to the project
    When I delete the todo
    Then the status code 200 is received
    And fetching the todo returns status code 404
    And the project still exists

    Examples:
      | project         |
      | Course project  |
      | Home renovation |

  # Error Flow
  @story3 @error
  Scenario Outline: Deleting a todo twice is rejected the second time
    Given the todo has doneStatus "<done>"
    And I have already deleted the todo
    When I delete the todo
    Then the status code 404 is received
    And the number of todos has decreased by one

    Examples:
      | done  |
      | false |
      | true  |
