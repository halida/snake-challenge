Feature: Can Create A New Map
  Background:
    Given I am on the new map page
    And I fill in "Title" with "A Brave New Map"
    Then I press "Create Map"
  Scenario: A new map
    Then I should see "A new map was created"
    Then I should see "Map Editor: A Brave New Map"
    And I should see "created by Anonymous"
  Scenario: Creating a map with duplicate title
    Then I am on the new map page
    And I fill in "Title" with "A Brave New Map"
    Then I press "Create Map"
    Then I should see "Error creating the map"
