# Story 1 - Create a todo (POST /todos)
# Normal flow:     create with a title only
# Alternate flows: create with all fields; create using an XML body
# Error flows:     empty title; missing title

Feature: Create a todo
  As a user, I want to create a todo so that I can track a task

  Background:
    Given the API is responsive
    And I record the current number of todos

  # Normal Flow
  @story1 @normal
  Scenario Outline: Successfully create a todo with only a title
    When I create a todo with title "<title>"
    Then the status code 201 is received
    And the todo "<title>" exists in the system
    And the todo "<title>" has default doneStatus and description
    And the number of todos has increased by one

    Examples:
      | title             |
      | Buy groceries     |
      | Submit lab report |

  # Alternate Flow
  @story1 @alternate
  Scenario Outline: Successfully create a todo with all fields
    When I create a todo titled "<title>" with doneStatus "<done>" and description "<description>"
    Then the status code 201 is received
    And the todo "<title>" is stored with doneStatus "<done>" and description "<description>"
    And the number of todos has increased by one

    Examples:
      | title           | done  | description        |
      | Read chapter 4  | true  | Chapters 4 and 5   |
      | Email professor | false | Ask about deadline |

  # Alternate Flow
  @story1 @alternate
  Scenario Outline: Successfully create a todo using an XML body
    When I create a todo with title "<title>" using XML
    Then the status code 201 is received
    And the todo "<title>" exists in the system
    And the number of todos has increased by one

    Examples:
      | title          |
      | Book flights   |
      | Renew passport |

  # Error Flow
  @story1 @error
  Scenario Outline: Reject a todo with an empty title
    When I try to create a todo with an empty title and description "<description>"
    Then the status code 400 is received
    And the error message contains "can not be empty"
    And the number of todos is unchanged

    Examples:
      | description       |
      | Has no real title |
      | Another attempt   |

  # Error Flow
  @story1 @error
  Scenario Outline: Reject a todo with no title
    When I try to create a todo with no title and description "<description>"
    Then the status code 400 is received
    And the error message contains "title"
    And the number of todos is unchanged

    Examples:
      | description         |
      | Missing title field |
      | Title left out      |
