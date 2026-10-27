# Story 5 - Link a todo to a project (POST /todos/:id/tasksof)
# Normal flow:     link a todo to a project, visible from both sides
# Alternate flows: unlink a todo that was already linked; link a todo to a category
# Error flows:     link or unlink with ids that do not exist, plus the bugs found with them
#
# Every scenario starts with one todo, "Linkable todo" (see Background).

Feature: Link a todo to a project
  As a user, I want to link a todo to a project so that I can group related tasks

  Background:
    Given the API is responsive
    And a todo exists with title "Linkable todo", doneStatus "false" and description "To be linked"

  # Normal Flow
  # The todo and the project start unlinked. After linking, each one shows the other.
  @story5 @normal
  Scenario Outline: Link a todo to a project
    Given a project exists with title "<project>"
    When I link the todo to the project
    Then the status code 201 is received
    And the todo shows the project in its tasksof relationship
    And the project shows the todo in its tasks relationship

    Examples:
      | project         |
      | Final exam prep |
      | Group project   |

  # Alternate Flow
  # The todo is already linked to the project. After unlinking, neither one shows the other.
  @story5 @alternate
  Scenario Outline: Unlink a todo that is already linked to a project
    Given a project exists with title "<project>"
    And the todo is linked to the project
    When I unlink the todo from the project
    Then the status code 200 is received
    And the todo no longer shows the project in its tasksof relationship
    And the project no longer shows the todo in its tasks relationship

    Examples:
      | project           |
      | Cancelled project |
      | Old semester      |

  # Alternate Flow
  # A category link works too, but only the todo side shows it (BUG-010).
  @story5 @alternate
  Scenario Outline: Link a todo to a category (visible from the todo side only, BUG-010)
    Given a category exists with title "<category>"
    When I link the todo to the category
    Then the status code 201 is received
    And the todo shows the category in its categories relationship
    And the category does not show the todo in its todos relationship

    Examples:
      | category |
      | School   |
      | Personal |

  # Error Flow
  # The project id does not exist, so linking is refused and the todo stays unlinked.
  @story5 @error
  Scenario Outline: Linking a todo to a non-existent project is rejected
    When I link the todo to a project with id <id>
    Then the status code 404 is received
    And the todo shows no project in its tasksof relationship

    Examples:
      | id      |
      | 99999   |
      | 1234567 |

  # Error Flow
  # The project id does not exist, so unlinking is refused.
  @story5 @error
  Scenario Outline: Unlinking a todo from a non-existent project is rejected
    When I unlink the todo from a project with id <id>
    Then the status code 404 is received

    Examples:
      | id      |
      | 99999   |
      | 1234567 |

  # Error Flow
  # BUG-012: the todo id in the URL does not exist.
  # Expected 404, but the API answers 400 with a null-pointer style message.
  @story5 @error
  Scenario Outline: Unlinking a non-existent todo from a project returns 400 instead of 404 (BUG-012)
    Given a project exists with title "Linking project"
    And the todo is linked to the project
    When I unlink the non-existent todo with id <id> from the project
    Then the status code 400 is received
    And the error message contains "is null"
    And the todo shows the project in its tasksof relationship

    Examples:
      | id      |
      | 99999   |
      | 1234567 |

  # Error Flow
  # BUG-013: the project id in the URL does not exist.
  # Expected 404, but the API answers 200 with the todos of another project.
  @story5 @error
  Scenario Outline: Querying the tasks of a non-existent project returns unrelated todos (BUG-013)
    When I request the tasks of the non-existent project with id <id>
    Then the status code 200 is received
    And the response lists todos instead of an error

    Examples:
      | id      |
      | 99999   |
      | 1234567 |

  # Error Flow
  # BUG-008 (found in Part A): the todo id in the URL does not exist.
  # Expected 404, but the API answers 200 with the existing projects.
  @story5 @error
  Scenario Outline: Querying the projects of a non-existent todo returns unrelated projects (BUG-008)
    Given a project exists with title "Linking project"
    And the todo is linked to the project
    When I request the tasksof of the non-existent todo with id <id>
    Then the status code 200 is received
    And the response lists the project

    Examples:
      | id      |
      | 99999   |
      | 1234567 |
