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
 * @fileoverview Service that handles routing for the exploration editor page.
 *
 * @author sll@google.com (Sean Lip)
 */

oppia.factory('routerService', [
    '$rootScope', '$location', '$window', '$timeout', '$interval', '$log', 'explorationInitStateNameService',
    'editorContextService', 'explorationStatesService', 'oppiaPlayerService',
    'explorationParamSpecsService', 'explorationTitleService', 'explorationData',
    function($rootScope, $location, $window, $timeout, $interval, $log, explorationInitStateNameService,
             editorContextService, explorationStatesService, oppiaPlayerService,
             explorationParamSpecsService, explorationTitleService, explorationData) {

  var MAIN_TAB = 'main';
  var PREVIEW_TAB = 'preview';
  var SETTINGS_TAB = 'settings';
  var STATS_TAB = 'stats';
  var HISTORY_TAB = 'history';
  var FEEDBACK_TAB = 'feedback';

  var _tabs = {
    active: MAIN_TAB
  };

  // When the URL path changes, reroute to the appropriate tab in the
  // exploration editor page.
  $rootScope.$watch(function() {
    return $location.path();
  }, function(newPath, oldPath) {
    if (newPath === '') {
      $location.path(oldPath);
      return;
    }

    if (!oldPath) {
      // This can happen when clicking on links whose href is "#".
      return;
    }

    $rootScope.$broadcast('externalSave');

    if (newPath === '/preview') {
      _tabs.active = PREVIEW_TAB;
    } else if (newPath === '/settings') {
      _tabs.active = SETTINGS_TAB;
      $rootScope.$broadcast('refreshSettingsTab');
    } else if (newPath === '/stats') {
      _tabs.active = STATS_TAB;
      $rootScope.$broadcast('refreshStatisticsTab');
    } else if (newPath === '/history') {
      // TODO(sll): Do this on-hover rather than on-click.
      $rootScope.$broadcast('refreshVersionHistory', {forceRefresh: false});
      _tabs.active = HISTORY_TAB;
    } else if (newPath === '/feedback') {
      _tabs.active = FEEDBACK_TAB;
    } else if (newPath.indexOf('/gui/') !== -1) {
      _tabs.active = MAIN_TAB;
      var putativeStateName = newPath.substring('/gui/'.length);

      var waitForStatesToLoad = $interval(function() {
        var allStates = explorationStatesService.getStates();
        if (allStates) {
          $interval.cancel(waitForStatesToLoad);

          if (allStates.hasOwnProperty(putativeStateName)) {
            editorContextService.setActiveStateName(putativeStateName);
            $rootScope.$broadcast('refreshStateEditor');
            // This seems to be needed in order to avoid the graph going off-center if
            // another tab is loaded first and then the user switches to the editor tab.
            $rootScope.$broadcast('redrawGraph');
          } else {
            $location.path('/gui/' + explorationInitStateNameService.savedMemento);
          }
        }
      }, 300);
    } else {
      if (explorationInitStateNameService.savedMemento) {
        $location.path('/gui/' + explorationInitStateNameService.savedMemento);
      }
    }
  });

  var _savePendingChanges = function() {
    try {
      $rootScope.$broadcast('externalSave');
    } catch (e) {
      // Sometimes, AngularJS throws a "Cannot read property $$nextSibling of
      // null" error. To get around this we must use $apply().
      $rootScope.$apply(function() {
        $rootScope.$broadcast('externalSave');
      });
    }
  };

  var _getCurrentStateFromLocationPath = function() {
    if ($location.path().indexOf('/gui/') !== -1) {
      return $location.path().substring('/gui/'.length);
    } else {
      return null;
    }
  };

  var routerService = {
    savePendingChanges: function() {
      _savePendingChanges();
    },
    getTabStatuses: function() {
      return _tabs;
    },
    isLocationSetToNonStateEditorTab: function() {
      var currentPath = $location.path();
      return (
        currentPath === '/preview' || currentPath === '/stats' ||
        currentPath === '/settings' || currentPath === '/history' ||
        currentPath === '/feedback');
    },
    getCurrentStateFromLocationPath: function() {
      return _getCurrentStateFromLocationPath();
    },
    navigateToMainTab: function(stateName) {
      _savePendingChanges();

      if (_getCurrentStateFromLocationPath() === stateName) {
        return;
      }

      var _actuallyNavigate = function(newStateName) {
        if (newStateName) {
          editorContextService.setActiveStateName(newStateName);
        }
        $location.path('/gui/' + editorContextService.getActiveStateName());
        $window.scrollTo(0, 0);
      };

      if (_tabs.active === MAIN_TAB) {
        $('.oppia-editor-cards-container').fadeOut(function() {
          _actuallyNavigate(stateName);
          $rootScope.$apply();
          $timeout(function() {
            $('.oppia-editor-cards-container').fadeIn();
          }, 150);
        });
      } else {
        _actuallyNavigate(stateName);
      }
    },
    navigateToPreviewTab: function() {
      _savePendingChanges();
      $location.path('/preview');
    },
    navigateToStatsTab: function() {
      _savePendingChanges();
      $location.path('/stats');
    },
    navigateToSettingsTab: function() {
      _savePendingChanges();
      $location.path('/settings');
    },
    navigateToHistoryTab: function() {
      _savePendingChanges();
      $location.path('/history');
    },
    navigateToFeedbackTab: function() {
      _savePendingChanges();
      $location.path('/feedback');
    }
  };

  return routerService;
}]);
