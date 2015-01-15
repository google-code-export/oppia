oppia.directive('chessPositionEditor', function($compile, warningsData) {
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
        $scope.properties = {
          whiteKingCastle: true,
          whiteQueenCastle: true,
          blackKingCastle: true,
          blackQueenCastle: true,
          toMove: 'b',
        } // board state properties

        $scope.getSuffix = function() {
          var suffix = " "; // rest of the FEN information from scope.properties
          p = $scope.properties;
          suffix += p.toMove + " "
          if (p.whiteKingCastle || p.whiteQueenCastle || // rules for castling
              p.blackKingCastle || p.blackQueenCastle) {
            if (p.whiteKingCastle) {
              suffix += "K";
            }
            if (p.whiteQueenCastle) {
              suffix += "Q";
            }
            if (p.blackKingCastle) {
              suffix += "k";
            }
            if (p.blackQueenCastle) {
              suffix += "q";
            }
            suffix += " ";
          }
          else {
            suffix += "- ";
          }
          suffix += "- "; // en passant currently unimplemented
          suffix += "0 "; // tracking halfmoves for draw, irrelevant
          suffix += "1"; // move number, irrelevant
          return suffix;
        }

        $scope.currentFEN = "" // board FEN position

        $scope.$watch( function () {
            return $scope.properties // on editing one of the properties
          },
          function(newValue) {
            if (newValue) {
              $scope.$parent.value = $scope.currentFEN + $scope.getSuffix();
            }
          }
        );

        $scope.onChange = function(oldPos, newPos) {
          $scope.currentFEN = ChessBoard.objToFen(newPos);
          $scope.$parent.value = $scope.currentFEN + $scope.getSuffix();
        };

        var boardConfig = {
          draggable: true,
          position: 'start',
          dropOffBoard: 'trash',
          sparePieces: true,
          onChange: $scope.onChange
        };

        $scope.alwaysEditable = true;

        // make sure the editor partial is loaded, then load chess board js and css
        $scope.$watch( function() {
            return angular.element('#chess-editor-board').length
          },
          function(newValue) {
            if (newValue)
              var board = new ChessBoard('chess-editor-board', boardConfig);
          }
        );
      }]
    };
  }
);
