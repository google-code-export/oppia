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
 * Directive for the TextInput interactive widget.
 *
 * IMPORTANT NOTE: The naming convention for customization args that are passed
 * into the directive is: the name of the parameter, followed by 'With',
 * followed by the name of the arg.
 */
oppia.directive('oppiaInteractiveChessInput', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'interactiveWidget/ChessInput',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        $scope.onChange = function(oldPos, newPos) {
          console.log(oldPos, newPos)
          if (!$.isEmptyObject(oldPos)) { // do not fire on initialization
            $scope.$parent.$parent.submitAnswer(ChessBoard.objToFen(newPos), 'submit');
          }
        };

        var boardConfig = {
          draggable: true,
          onChange: $scope.onChange
        };
        
        var board = new ChessBoard('input-chess-board', boardConfig);
        board.position(oppiaHtmlEscaper.escapedJsonToObj($attrs.chessWithValue));
      }]
    };
  }
]);


oppia.directive('oppiaResponseChessInput', [
  'oppiaHtmlEscaper', function(oppiaHtmlEscaper) {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'response/ChessInput',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        console.log($scope)
        $scope.answer = oppiaHtmlEscaper.escapedJsonToObj($attrs.answer);

        var boardConfig = {
          draggable: true,
          onChange: $scope.onChange
        };
        
        $scope.$watch( function() { // only render board once html is loaded
            return angular.element('#response-board-' + $scope.$id).length
          }, function(newValue, oldValue) {
            if (newValue != 0) {
              var board = new ChessBoard('response-board-' + $scope.$id, boardConfig);
              board.position($scope.answer);
            }
          }
        );
      }]
    };
  }
]);
