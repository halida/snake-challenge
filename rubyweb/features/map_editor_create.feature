Feature: Can Create A New Map
  Scenario:
    Given I am on the new map page
    And I fill in "Title" with "A Brave New Map"
    Then I press "Create Map"
    Then I should see "Map Editor: A Brave New Map"
    And I should see "created by Anonymous"
