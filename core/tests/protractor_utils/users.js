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
 * @fileoverview Utilities for user creation, login and privileging when
 * carrying out end-to-end testing with protractor.
 *
 * @author Jacob Davis (jacobdavis11@gmail.com)
 */

var forms = require('./forms.js');
var general = require('./general.js');
var admin = require('./admin.js');

var login = function(email, isSuperAdmin) {
  // Use of element is not possible because the login page is non-angular.
  // The full url is also necessary.
  var driver = protractor.getInstance().driver;
  driver.get(general.SERVER_URL_PREFIX + general.LOGIN_URL_SUFFIX);

  driver.findElement(protractor.By.name('email')).clear();
  driver.findElement(protractor.By.name('email')).sendKeys(email);
  if (isSuperAdmin) {
    driver.findElement(protractor.By.name('admin')).click();
  }
  driver.findElement(protractor.By.id('submit-login')).click();
};

var logout = function() {
  var driver = protractor.getInstance().driver;
  driver.get(general.SERVER_URL_PREFIX + general.LOGIN_URL_SUFFIX);
  driver.findElement(protractor.By.id('submit-logout')).click();
};

// The user needs to log in immediately before this method is called. Note
// that this will fail if the user already has a username.
var _completeSignup = function(username) {
  browser.get('/signup?return_url=http%3A%2F%2Flocalhost%3A4445%2F');
  element(by.css('.protractor-test-username-input')).sendKeys(username);
  element(by.css('.protractor-test-agree-to-terms-checkbox')).click();
  element(by.css('.protractor-test-register-user')).click();
};

var createUser = function(email, username) {
  login(email);
  _completeSignup(username);
  logout();
};

var createAndLoginUser = function(email, username) {
  login(email);
  _completeSignup(username);
};

var createModerator = function(email, username) {
  login(email, true);
  _completeSignup(username);
  admin.editConfigProperty(
      'Email addresses of moderators', 'List', function(listEditor) {
    listEditor.addItem('Unicode').setValue(email);
  });
  logout();
};

var createAdmin = function(email, username) {
  login(email, true);
  _completeSignup(username);
  admin.editConfigProperty(
      'Email addresses of admins', 'List', function(listEditor) {
    listEditor.addItem('Unicode').setValue(email);
  });
  logout();
};

exports.login = login;
exports.logout = logout;
exports.createUser = createUser;
exports.createAndLoginUser = createAndLoginUser;
exports.createModerator = createModerator;
exports.createAdmin = createAdmin;

