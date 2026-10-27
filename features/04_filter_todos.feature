# Story 4 - Filter todos by status (GET /todos?doneStatus=...)
# Normal flow:     filter by doneStatus
# Alternate flows: combined filters; filter with no matches gives an empty list
# Error flows:     invalid doneStatus value
#
# Note on the error flow: the API returns 200 with an empty list for an invalid
# doneStatus filter instead of a 400 (BUG-005). The scenario asserts the actual
# behaviour so the suite stays green and the bug stays documented.

Feature: Filter todos by status
  As a user, I want to filter my todos so that I can focus on what is done or still open

  Background:
    Given the API is responsive
    And the following todos exist:
      | title          | doneStatus | description |
      | Filter open A  | false      | open        |
      | Filter open B  | false      | open        |
      | Filter done A  | true       | done        |

  # Normal Flow
  # "appear" lists the todos that must be in the results, "not appear" the ones that must be left out
  @story4 @normal
  Scenario Outline: Filter todos by doneStatus
    When I filter todos by doneStatus "<done>"
    Then the status code 200 is received
    And the filtered results include "<should appear>"
    And the filtered results do not include "<should not appear>"
    And every filtered todo has doneStatus "<done>"

    Examples:
      | done  | should appear               | should not appear |
      | false | Filter open A,Filter open B | Filter done A     |
      | true  | Filter done A               | Filter open A     |

  # Alternate Flow
  # the title filter is an exact match, so exactly one todo comes back
  @story4 @alternate
  Scenario Outline: Combine doneStatus and title filters
    When I filter todos by doneStatus "<done>" and title "<title>"
    Then the status code 200 is received
    And the only filtered todo is "<title>"

    Examples:
      | done  | title         |
      | false | Filter open A |
      | false | Filter open B |
      | true  | Filter done A |

  # Alternate Flow
  @story4 @alternate
  Scenario Outline: A filter with no matches returns an empty list
    When I filter todos by title "<title>"
    Then the status code 200 is received
    And the filtered results are empty

    Examples:
      | title                  |
      | No such todo anywhere  |
      | Filter open            |

  # Error Flow
  @story4 @error
  Scenario Outline: An invalid doneStatus filter returns an empty list (BUG-005)
    When I filter todos by doneStatus "<bad_value>"
    Then the status code 200 is received
    And the filtered results are empty

    Examples:
      | bad_value    |
      | notaboolean  |
      | 42           |
