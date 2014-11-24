oppia.directive('chessEditor', function($compile, warningsData) {
  return {
      link: function(scope, element, attrs) {
        scope.getTemplateUrl = function() {
          return OBJECT_EDITOR_TEMPLATES_URL + scope.$parent.objType;
        };
        $compile(element.contents())(scope);
      },
      restrict: 'E',
      scope: {},
      template: '<span ng-include="getTemplateUrl()"></span>',
      controller: ['$scope', '$attrs', function($scope, $attrs) {
        $scope.onChange = function(oldPos, newPos) {
          $scope.$parent.$parent.submitAnswer(ChessBoard.objToFen(newPos), 'submit');
        };

        var cfg = {
          draggable: true,
          position: 'start',
          onChange: $scope.onChange
        };
        
        var board = new ChessBoard('board', cfg);
        $scope.alwaysEditable = true;
      }]
    };
  }
);
