// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Tools for displaying and awarding ratings.
 *
 * @author Jacob Davis
 */

oppia.directive('ratingFromValue', [function($http) {
  return {
    // This will display a star-rating based on the given data. Exactly one of
    // 'ratingValue' and 'ratingFrequencies' should be specified.
    //  - ratingValue: an integer 1-5 giving the rating
    //  - ratingFrequencies: a dictionary with keys '1' to '5' giving the
    //    number of times each rating has been awarded; from this the average
    //    rating will be computed and displayed.
    //  - isEditable: true or false; whether the rating is user-editable.
    //  - onEdit: should be supplied iff isEditable is true, and be a function
    //    that will be supplied with the new rating when the rating is changed.
    restrict: 'E',
    scope: {
      ratingValue: '=',
      isEditable: '=',
      onEdit: '='
    },
    templateUrl: 'rating/fromValue',
    controller: ['$scope', function($scope) {
      var POSSIBLE_RATINGS = [1, 2, 3, 4, 5];
      $scope.stars = POSSIBLE_RATINGS.map(function(starValue) {
        return {
          style: 'glyphicon-star-empty',
          value: starValue
        };
      });

      var displayValue = function(ratingValue) {
        for (var i = 0; i < $scope.stars.length; i++) {
          $scope.stars[i].style =
            ratingValue === undefined ? 'glyphicon-star-empty' :
            ratingValue < $scope.stars[i].value  - 0.5 ?
            'glyphicon-star-empty' :
            'glyphicon-star';
        }
      };

      displayValue($scope.ratingValue);
      $scope.$watch('ratingValue', function() {
        displayValue($scope.ratingValue);
      });

      $scope.clickStar = function(starValue) {
        if ($scope.isEditable) {
          $scope.ratingValue = starValue;
          displayValue(starValue);
          $scope.onEdit(starValue);
        }
      };
      $scope.enterStar = function(starValue) {
        if ($scope.isEditable) {
          displayValue(starValue);
        }
      };
      $scope.leaveStar = function(starValue) {
        if ($scope.isEditable) {
          displayValue($scope.ratingValue);
        }
      };
    }]
  };
}]);


oppia.directive('ratingFromFrequencies', [function() {
  return {
    restrict: 'E',
    scope: {
      ratingFrequencies: '&',
      isEditable: '=',
      onEdit: '='
    },
    templateUrl: 'rating/fromFrequencies',
    controller: ['$scope', function($scope) {
      $scope.computeAverageRating = function(ratingFrequencies) {
        var MINIMUM_ACCEPTABLE_NUMBER_OF_RATINGS = 5;
        totalValue = 0.0;
        totalNumber = 0;
        for (var value in ratingFrequencies) {
          totalValue += value * ratingFrequencies[value];
          totalNumber += ratingFrequencies[value];
        }
        return totalNumber >= MINIMUM_ACCEPTABLE_NUMBER_OF_RATINGS ?
          totalValue / totalNumber : undefined;
      };

      $scope.ratingValue = $scope.computeAverageRating(
        $scope.ratingFrequencies());
    }]
  };
}]);
