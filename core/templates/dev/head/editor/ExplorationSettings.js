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
 * @fileoverview Controllers for the exploration settings tab.
 *
 * @author sll@google.com (Sean Lip)
 */

oppia.controller('ExplorationSettings', [
    '$scope', '$http', '$window', '$modal', '$rootScope', 'activeInputData', 'explorationData',
    'explorationTitleService', 'explorationCategoryService',
    'explorationObjectiveService', 'explorationLanguageCodeService', 'explorationRightsService',
    'explorationInitStateNameService', 'explorationParamSpecsService', 'changeListService',
    'warningsData', 'explorationStatesService', function(
      $scope, $http, $window, $modal, $rootScope, activeInputData, explorationData,
      explorationTitleService, explorationCategoryService,
      explorationObjectiveService, explorationLanguageCodeService, explorationRightsService,
      explorationInitStateNameService, explorationParamSpecsService, changeListService,
      warningsData, explorationStatesService) {

  var GALLERY_PAGE_URL = '/gallery';
  var EXPLORE_PAGE_PREFIX = '/explore/';

  $scope.getExplorePageUrl = function() {
    return (
      window.location.protocol + '//' + window.location.host +
      EXPLORE_PAGE_PREFIX + $scope.explorationId);
  };

  $scope.initSettingsTab = function() {
    $scope.explorationTitleService = explorationTitleService;
    $scope.explorationCategoryService = explorationCategoryService;
    $scope.explorationObjectiveService = explorationObjectiveService;
    $scope.explorationLanguageCodeService = explorationLanguageCodeService;
    $scope.explorationRightsService = explorationRightsService;
    $scope.explorationInitStateNameService = explorationInitStateNameService;
    $scope.explorationParamSpecsService = explorationParamSpecsService;

    explorationData.getData().then(function(data) {
      $scope.explorationParamChanges = data.param_changes || [];
      $scope.refreshSettingsTab();
    });
  };

  $scope.refreshSettingsTab = function() {
    var _states = explorationStatesService.getStates();
    // Ensure that explorationStatesService has been initialized before getting
    // the state names from it. (Otherwise, navigating to the settings tab
    // directly (by entering a URL that ends with /settings) results in a
    // console error.
    if (_states) {
      $scope.stateNames = Object.keys(_states);
    }
  };

  $scope.$on('refreshSettingsTab', $scope.refreshSettingsTab);

  $scope.initSettingsTab();

  $scope.ROLES = [
    {name: 'Manager (can edit permissions)', value: 'owner'},
    {name: 'Collaborator (can make changes)', value: 'editor'},
    {name: 'Playtester (can give feedback)', value: 'viewer'}
  ];

  $scope.saveExplorationTitle = function() {
    explorationTitleService.saveDisplayedValue();
  };

  $scope.saveExplorationCategory = function() {
    explorationCategoryService.saveDisplayedValue();
  };

  $scope.saveExplorationObjective = function() {
    explorationObjectiveService.saveDisplayedValue();
  };

  $scope.saveExplorationLanguageCode = function() {
    explorationLanguageCodeService.saveDisplayedValue();
  };

  $scope.saveExplorationInitStateName = function() {
    var newInitStateName = explorationInitStateNameService.displayed;

    if (!explorationStatesService.getState(newInitStateName)) {
      warningsData.addWarning('Invalid initial state name: ' + newInitStateName);
      explorationInitStateNameService.restoreFromMemento();
      return;
    }

    explorationInitStateNameService.saveDisplayedValue();

    $rootScope.$broadcast('refreshGraph');
  };

  $scope.saveExplorationParamChanges = function(newValue, oldValue) {
    if (!angular.equals(newValue, oldValue)) {
      changeListService.editExplorationProperty(
        'param_changes', newValue, oldValue);
    }
  };

  // TODO(sll): Modify this so that it works correctly when discarding changes
  // to the default skin id.
  $scope.$watch('$parent.defaultSkinId', function(newValue, oldValue) {
    if (oldValue !== undefined && !angular.equals(newValue, oldValue)) {
      changeListService.editExplorationProperty(
        'default_skin_id', newValue, oldValue);
    }
  });

  /********************************************
  * Methods for rights management.
  ********************************************/
  $scope.openEditRolesForm = function() {
    activeInputData.name = 'explorationMetadata.editRoles';
    $scope.newMemberUsername = '';
    $scope.newMemberRole = $scope.ROLES[0];
  };

  $scope.closeEditRolesForm = function() {
    $scope.newMemberUsername = '';
    $scope.newMemberRole = $scope.ROLES[0];
    activeInputData.clear();
  };

  $scope.editRole = function(newMemberUsername, newMemberRole) {
    activeInputData.clear();
    explorationRightsService.saveChangeToBackend({
      new_member_username: newMemberUsername,
      new_member_role: newMemberRole
    });
  };

  $scope.toggleViewabilityIfPrivate = function() {
    explorationRightsService.saveChangeToBackend({
      viewable_if_private: !explorationRightsService.viewableIfPrivate()
    });
  };

  /********************************************
  * Methods relating to control buttons.
  ********************************************/
  $scope.showTransferExplorationOwnershipModal = function() {
    warningsData.clear();
    $modal.open({
      templateUrl: 'modals/transferExplorationOwnership',
      backdrop: true,
      controller: ['$scope', '$modalInstance', function($scope, $modalInstance) {
          $scope.transfer = $modalInstance.close;

          $scope.cancel = function() {
            $modalInstance.dismiss('cancel');
            warningsData.clear();
          };
        }
      ]
    }).result.then(function() {
      explorationRightsService.saveChangeToBackend({is_community_owned: true});
    });
  };

  $scope.showNominateExplorationModal = function() {
    warningsData.clear();
    $modal.open({
      templateUrl: 'modals/nominateExploration',
      backdrop: true,
      controller: ['$scope', '$modalInstance', function($scope, $modalInstance) {
        $scope.close = function() {
          $modalInstance.dismiss('cancel');
          warningsData.clear();
        };
      }]
    });
  };

  $scope.deleteExploration = function(role) {
    warningsData.clear();

    $modal.open({
      templateUrl: 'modals/deleteExploration',
      backdrop: true,
      controller: ['$scope', '$modalInstance', function($scope, $modalInstance) {
        $scope.reallyDelete = $modalInstance.close;

        $scope.cancel = function() {
          $modalInstance.dismiss('cancel');
          warningsData.clear();
        };
      }]
    }).result.then(function() {
      var deleteUrl = $scope.explorationDataUrl;
      if (role) {
        deleteUrl += ('?role=' + role);
      }
      $http['delete'](deleteUrl).success(function(data) {
        $window.location = GALLERY_PAGE_URL;
      });
    });
  };

  $scope.publicizeExploration = function() {
    explorationRightsService.saveChangeToBackend({is_publicized: true});
  };

  $scope.unpublicizeExploration = function() {
    explorationRightsService.saveChangeToBackend({is_publicized: false});
  };

  $scope.unpublishExploration = function() {
    explorationRightsService.saveChangeToBackend({is_public: false});
  };

  $scope.isExplorationLockedForEditing = function() {
    return changeListService.isExplorationLockedForEditing();
  };
}]);
