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
 * @fileoverview Directive for the rule editor.
 *
 * @author sll@google.com (Sean Lip)
 */

oppia.directive('ruleTypeSelector', [function() {
  return {
    restrict: 'E',
    scope: {
      allRuleTypes: '&',
      localValue: '=',
      onSelectionChange: '&',
      canAddDefaultRule: '&'
    },
    template: '<input type="hidden">',
    controller: [
        '$scope', '$element', '$rootScope', '$filter',
        function($scope, $element, $rootScope, $filter) {

      var choices = [];
      var numberOfRuleTypes = 0;
      for (var ruleType in $scope.allRuleTypes()) {
        numberOfRuleTypes++;
        choices.push({
          id: ruleType,
          text: 'Answer ' + $filter('replaceInputsWithEllipses')(ruleType)
        });
      }

      choices.sort(function(a, b) {
        if (a.text < b.text) {
          return -1;
        } else if (a.text > b.text) {
          return 1;
        } else {
          return 0;
        }
      });

      if ($scope.canAddDefaultRule()) {
        choices.unshift({
          id: 'Default',
          text: 'When no other rule applies...'
        });
      }

      if (!$scope.localValue) {
        $scope.localValue = choices[0].id;
      }

      var select2Node = $element[0].firstChild;
      $(select2Node).select2({
        data: choices,
        // Suppress the search box.
        minimumResultsForSearch: -1,
        allowClear: false,
        width: '210px',
        formatSelection: function(object, container) {
          if (object.id === 'Default') {
            return 'When no other rule applies';
          } else {
            return 'Answer ' + $filter('truncateAtFirstInput')(object.id);
          }
        }
      });

      // Initialize the dropdown.
      $(select2Node).select2('val', $scope.localValue);

      // Update $scope.localValue when the selection changes.
      $(select2Node).on('change', function(e) {
        $scope.localValue = e.val;
        // This is needed to actually update the localValue in the containing
        // scope.
        $scope.$apply();
        $scope.onSelectionChange();
        // This is needed to propagate the change and display input fields for
        // parameterizing the rule.
        $scope.$apply();
      });
    }]
  };
}]);


oppia.directive('ruleEditor', ['$log', function($log) {
  return {
    restrict: 'E',
    scope: {
      rule: '=',
      saveRule: '&',
      deleteRule: '&',
      isEditable: '='
    },
    templateUrl: 'inline/rule_editor',
    controller: [
      '$scope', '$rootScope', '$modal', '$timeout', 'editorContextService', 'routerService',
      'validatorsService', 'rulesService', 'explorationStatesService', 'stateInteractionIdService',
      function(
          $scope, $rootScope, $modal, $timeout, editorContextService, routerService,
          validatorsService, rulesService, explorationStatesService, stateInteractionIdService) {
        $scope.editRuleForm = {};

        $scope.answerChoices = rulesService.getAnswerChoices();
        $scope.currentInteractionId = stateInteractionIdService.savedMemento;

        $scope.ruleDestMemento = null;
        $scope.ruleDescriptionMemento = null;
        $scope.ruleDefinitionMemento = null;
        $scope.ruleFeedbackMemento = null;

        $scope.ruleEditorIsOpen = false;
        $scope.openRuleEditor = function() {
          if ($scope.isEditable) {
            $scope.ruleDescriptionMemento = angular.copy($scope.rule.description);
            $scope.ruleDefinitionMemento = angular.copy($scope.rule.definition);
            $scope.ruleFeedbackMemento = angular.copy($scope.rule.feedback);
            $scope.ruleDestMemento = angular.copy($scope.rule.dest);

            $scope.ruleEditorIsOpen = true;
            if ($scope.rule.feedback.length === 0) {
              $scope.rule.feedback.push('');
            }
          }
        };

        $scope.ruleDescriptionMemento = null;
        $scope.ruleDefinitionMemento = null;

        $scope.saveThisRule = function() {
          $scope.$broadcast('saveRuleDetails');
          // TODO(sll): Add more validation prior to saving.
          $scope.ruleEditorIsOpen = false;

          $scope.ruleDescriptionMemento = null;
          $scope.ruleDefinitionMemento = null;
          $scope.ruleFeedbackMemento = null;
          $scope.ruleDestMemento = null;

          $scope.saveRule();
        };
        $scope.cancelThisEdit = function() {
          $scope.ruleEditorIsOpen = false;
          $scope.rule.description = angular.copy($scope.ruleDescriptionMemento);
          $scope.rule.definition = angular.copy($scope.ruleDefinitionMemento);
          $scope.rule.feedback = angular.copy($scope.ruleFeedbackMemento);
          $scope.rule.dest = angular.copy($scope.ruleDestMemento);
          $scope.ruleDescriptionMemento = null;
          $scope.ruleDefinitionMemento = null;
          $scope.ruleFeedbackMemento = null;
          $scope.ruleDestMemento = null;
        };
        $scope.deleteThisRule = function() {
          $scope.deleteRule();
        };

        $scope.$on('externalSave', function() {
          if ($scope.ruleEditorIsOpen) {
            $scope.saveThisRule();
          }
        });

        $scope.getActiveStateName = function() {
          return editorContextService.getActiveStateName();
        };

        $scope.isRuleConfusing = function() {
          return (
            $scope.rule.feedback.length === 0 &&
            $scope.rule.dest === editorContextService.getActiveStateName());
        };

        $scope.navigateToRuleDest = function() {
          routerService.navigateToMainTab($scope.rule.dest);
        };

        $scope.isRuleEmpty = function(rule) {
          var hasFeedback = false;
          for (var i = 0; i < rule.feedback.length; i++) {
            if (rule.feedback[i].length > 0) {
              hasFeedback = true;
            }
          }

          return (
            rule.dest === editorContextService.getActiveStateName() &&
            !hasFeedback);
        };
      }
    ]
  };
}]);


oppia.directive('ruleDetailsEditor', ['$log', function($log) {
  return {
    restrict: 'E',
    scope: {
      rule: '=',
      canAddDefaultRule: '&'
    },
    templateUrl: 'rules/ruleDetailsEditor',
    controller: [
      '$scope', '$rootScope', '$modal', '$timeout', 'editorContextService', 'routerService',
      'validatorsService', 'rulesService', 'explorationStatesService',
      function(
          $scope, $rootScope, $modal, $timeout, editorContextService, routerService,
          validatorsService, rulesService, explorationStatesService) {

        $scope.RULE_FEEDBACK_SCHEMA = {
          type: 'list',
          items: {
            type: 'html',
            ui_config: {
              size: 'small'
            }
          },
          ui_config: {
            add_element_text: 'Add Variation'
          }
        };

        var lastSetRuleDest = $scope.rule.dest;

        // We use a slash because this character is forbidden in a state name.
        var _PLACEHOLDER_RULE_DEST = '/';

        $scope.$on('saveRuleDetails', function() {
          // Remove null feedback.
          var nonemptyFeedback = [];
          for (var i = 0; i < $scope.rule.feedback.length; i++) {
            if ($scope.rule.feedback[i]) {
              nonemptyFeedback.push($scope.rule.feedback[i]);
            }
          }
          $scope.rule.feedback = nonemptyFeedback;
        });

        $scope.createNewDestIfNecessary = function() {
          if ($scope.rule.dest === _PLACEHOLDER_RULE_DEST) {
            $modal.open({
              templateUrl: 'modals/addState',
              backdrop: true,
              resolve: {},
              controller: [
                  '$scope', '$timeout', '$modalInstance', 'explorationStatesService', 'focusService',
                  function($scope, $timeout, $modalInstance, explorationStatesService, focusService) {
                $scope.newStateName = '';
                $timeout(function() {
                  focusService.setFocus('newStateNameInput');
                });

                $scope.isNewStateNameValid = function(newStateName) {
                  return explorationStatesService.isNewStateNameValid(newStateName, false);
                }

                $scope.submit = function(newStateName) {
                  if (!$scope.isNewStateNameValid(newStateName, false)) {
                    return;
                  }

                  $modalInstance.close({
                    action: 'addNewState',
                    newStateName: newStateName
                  });
                };

                $scope.cancel = function() {
                  $modalInstance.close({
                    action: 'cancel'
                  });
                };
              }]
            }).result.then(function(result) {
              if (result.action === 'addNewState') {
                $scope.reloadingDestinations = true;
                explorationStatesService.addState(result.newStateName, function() {
                  $rootScope.$broadcast('refreshGraph');
                  $timeout(function() {
                    $scope.rule.dest = result.newStateName;
                    lastSetRuleDest = $scope.rule.dest;
                    // Reload the dropdown to include the new state.
                    $scope.reloadingDestinations = false;
                  });
                });
              } else if (result.action === 'cancel') {
                $scope.rule.dest = lastSetRuleDest;
              } else {
                throw 'Invalid result action from add state modal: ' + result.action;
              }
            });
          } else {
            lastSetRuleDest = $scope.rule.dest;
          }
        };

        $scope.isDefaultRule = function() {
          return ($scope.rule.description === 'Default');
        };

        $scope.destChoices = [];
        $scope.$watch(explorationStatesService.getStates, function(newValue) {
          var _currentStateName = editorContextService.getActiveStateName();

          // This is a list of objects, each with an ID and name. These
          // represent all states, including 'END', as well as an option to
          // create a new state.
          $scope.destChoices = [{
            id: _currentStateName,
            text: _currentStateName + ' ⟳'
          }, {
            id: _PLACEHOLDER_RULE_DEST,
            text: 'Create New State...'
          }];

          var stateNames = Object.keys(explorationStatesService.getStates()).sort();
          stateNames.push(END_DEST);
          for (var i = 0; i < stateNames.length; i++) {
            if (stateNames[i] !== _currentStateName) {
              $scope.destChoices.push({
                id: stateNames[i],
                text: stateNames[i]
              });
            }
          }
        }, true);
      }
    ]
  };
}]);


oppia.directive('ruleDescriptionEditor', ['$log', function($log) {
  return {
    restrict: 'E',
    scope: {
      currentRuleDescription: '=',
      currentRuleDefinition: '=',
      canAddDefaultRule: '&'
    },
    templateUrl: 'rules/ruleDescriptionEditor',
    controller: [
        '$scope', 'editorContextService', 'explorationStatesService', 'routerService', 'validatorsService',
        'rulesService',
        function($scope, editorContextService, explorationStatesService, routerService, validatorsService, rulesService) {
      var _generateAllRuleTypes = function() {
        var _interactionHandlerSpecs = rulesService.getInteractionHandlerSpecs();
        for (var i = 0; i < _interactionHandlerSpecs.length; i++) {
          if (_interactionHandlerSpecs[i].name == 'submit') {
            $scope.allRuleTypes = {};
            for (var description in _interactionHandlerSpecs[i].rules) {
              $scope.allRuleTypes[description] = _interactionHandlerSpecs[i].rules[description].classifier;
            }
            return;
          }
        }
      };

      var _computeRuleDescriptionFragments = function() {
        if (!$scope.currentRuleDescription) {
          $scope.ruleDescriptionFragments = [];
          return;
        }

        var pattern = /\{\{\s*(\w+)\s*\|\s*(\w+)\s*\}\}/;

        var finalInputArray = $scope.currentRuleDescription.split(pattern);
        if (finalInputArray.length % 3 !== 1) {
          $log.error('Could not process rule description.');
        }

        var result = [];
        for (var i = 0; i < finalInputArray.length; i += 3) {
          result.push({
            type: 'noneditable',
            // Omit the leading noneditable string.
            text: i !== 0 ? finalInputArray[i] : ''
          });
          if (i == finalInputArray.length - 1) {
            break;
          }

          var _answerChoices = rulesService.getAnswerChoices();

          if (_answerChoices) {
            // This rule is for a multiple-choice or image-click interaction.
            // TODO(sll): Remove the need for this special case.
            if (_answerChoices.length > 0) {
              $scope.ruleDescriptionChoices = _answerChoices.map(function(choice, ind) {
                return {
                  val: choice.label,
                  id: choice.val
                };
              });
              result.push({'type': 'select', 'varName': finalInputArray[i+1]});
              if (!$scope.currentRuleDefinition.inputs[finalInputArray[i + 1]]) {
                $scope.currentRuleDefinition.inputs[finalInputArray[i + 1]] = $scope.ruleDescriptionChoices[0].id;
              }
            } else {
              $scope.ruleDescriptionChoices = [];
              result.push({'type': 'noneditable', 'text': ' [Error: No choices available] '});
            }
          } else {
            result.push({
              'type': finalInputArray[i+2],
              'varName': finalInputArray[i+1]
            });
          }
        }
        $scope.ruleDescriptionFragments = result;
      };

      $scope.onSelectNewRuleType = function() {
        $scope.currentRuleDefinition.name = $scope.allRuleTypes[$scope.currentRuleDescription];
        $scope.currentRuleDefinition.inputs = {};
        _computeRuleDescriptionFragments();

        // Finds the parameters and sets them in $scope.currentRuleDefinition.inputs.
        var pattern = /\{\{\s*(\w+)\s*(\|\s*\w+\s*)?\}\}/;
        var copyOfRule = $scope.currentRuleDescription;
        while (true) {
          if (!copyOfRule.match(pattern)) {
            break;
          }
          var varName = copyOfRule.match(pattern)[1];
          var varType = null;
          if (copyOfRule.match(pattern)[2]) {
            varType = copyOfRule.match(pattern)[2].substring(1);
          }

          if (varType == 'Set') {
            $scope.currentRuleDefinition.inputs[varName] = [];
          } else if (varType == 'NonnegativeInt') {
            // Set a default value.
            $scope.currentRuleDefinition.inputs[varName] = 0;
          } else if (varType == "Graph") {
            $scope.currentRuleDefinition.inputs[varName] = {
              'vertices': [],
              'edges': [],
              'isDirected': false,
              'isWeighted': false,
              'isLabeled': false
            };
          } else {
            $scope.currentRuleDefinition.inputs[varName] = '';
          }

          copyOfRule = copyOfRule.replace(pattern, ' ');
        }
      };

      _generateAllRuleTypes();
      if ($scope.currentRuleDescription === null) {
        for (var key in $scope.allRuleTypes) {
          if ($scope.currentRuleDescription === null || key < $scope.currentRuleDescription) {
            $scope.currentRuleDescription = key;
          }
        }
        $scope.onSelectNewRuleType();
      }

      _computeRuleDescriptionFragments();

      $scope.$watch('rulesService.interactionHandlerSpecs', function() {
        _generateAllRuleTypes();
      });
    }]
  };
}]);
