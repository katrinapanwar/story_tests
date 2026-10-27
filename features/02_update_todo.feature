# Story 2 - Update a todo (POST /todos/:id to amend, PUT /todos/:id to replace)
# Normal flow:     amend only doneStatus, other fields are kept
# Alternate flows: full replacement with PUT (omitted fields are reset)
# Error flows:     amend a non-existent id; non-boolean doneStatus

Feature: Update a todo
  As a user, I want to update a todo so that it reflects the current state of my task

  Background:
    Given the API is responsive
    And a todo exists with title "Original title", doneStatus "false" and description "Original description"

  # Normal Flow
  @story2 @normal
  Scenario Outline: Mark a todo as done without changing its other fields
    When I amend the todo setting doneStatus to "<done>"
    Then the status code 200 is received
    And the todo is stored with title "Original title", doneStatus "<done>" and description "Original description"

    Examples:
      | done  |
      | true  |
      | false |

  # Alternate Flow
  @story2 @alternate
  Scenario Outline: Replace a todo completely with PUT
    When I replace the todo with title "<title>", doneStatus "<done>" and description "<description>"
    Then the status code 200 is received
    And the todo is stored with title "<title>", doneStatus "<done>" and description "<description>"

    Examples:
      | title         | done  | description     |
      | Replaced one  | true  | New description |
      | Replaced two  | false | Another one     |

  # Alternate Flow
  @story2 @alternate
  Scenario Outline: A PUT with only a title resets the omitted fields
    When I replace the todo with only the title "<title>"
    Then the status code 200 is received
    And the todo is stored with title "<title>", doneStatus "false" and description ""

    Examples:
      | title        |
      | Title only   |
      | Just a title |

  # Error Flow
  @story2 @error
  Scenario Outline: Amending a todo that does not exist is rejected
    When I amend the non-existent todo with id <id> setting title to "<title>"
    Then the status code 404 is received
    And the original todo is unchanged

    Examples:
      | id       | title        |
      | 99999    | Ghost todo   |
      | 1234567  | Missing todo |

  # Error Flow
  @story2 @error
  Scenario Outline: Amending a todo with a non-boolean doneStatus is rejected
    When I amend the todo setting doneStatus to "<bad_value>"
    Then the status code 400 is received
    And the original todo is unchanged

    Examples:
      | bad_value |
      | maybe     |
      | 123       |
