Feature: creating order via web
  Scenario: MongoDB database running
    Given a create order request
    Then the order is stored
    And messages are sent to other modules
