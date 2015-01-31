# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Sean Lip'

from core.domain import exp_domain
from core.domain import exp_services
from core.domain import param_domain
from core.domain import rights_manager
from core.domain import summary_services
from core.domain import user_services
from core.platform import models
(activity_models,) = models.Registry.import_models([models.NAMES.activity])
from core.tests import test_utils
import feconf


class SummaryServicesUnitTests(test_utils.GenericTestBase):
    """Test the summary services module."""

    EXP_ID = 'An_exploration_id'

    def setUp(self):
        """Before each individual test, create a dummy exploration."""
        super(SummaryServicesUnitTests, self).setUp()

        self.OWNER_ID = self.get_user_id_from_email(self.OWNER_EMAIL)
        self.EDITOR_ID = self.get_user_id_from_email(self.EDITOR_EMAIL)
        self.VIEWER_ID = self.get_user_id_from_email(self.VIEWER_EMAIL)

        user_services.get_or_create_user(self.OWNER_ID, self.OWNER_EMAIL)
        user_services.get_or_create_user(self.EDITOR_ID, self.EDITOR_EMAIL)
        user_services.get_or_create_user(self.VIEWER_ID, self.VIEWER_EMAIL)

        self.register_editor(self.OWNER_EMAIL, username=self.OWNER_USERNAME)
        self.register_editor(self.EDITOR_EMAIL, username=self.EDITOR_USERNAME)
        self.register_editor(self.VIEWER_EMAIL, username=self.VIEWER_USERNAME)

        self.set_admins([self.ADMIN_EMAIL])
        self.user_id_admin = self.get_user_id_from_email(self.ADMIN_EMAIL)


class ActivitySummaryTests(SummaryServicesUnitTests):
    """Test activity summaries."""

    ALBERT_EMAIL = 'albert@example.com'
    BOB_EMAIL = 'bob@example.com'
    ALBERT_NAME = 'albert'
    BOB_NAME = 'bob'

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    def test_is_activity_editable(self):
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)

        # Check that only the owner may edit.
        summary = summary_services.get_exploration_summary_by_id(self.EXP_ID)
        self.assertTrue(summary.is_editable_by(self.OWNER_ID))
        self.assertFalse(summary.is_editable_by(self.EDITOR_ID))
        self.assertFalse(summary.is_editable_by(self.VIEWER_ID))

        # Owner makes viewer a viewer and editor an editor.
        rights_manager.assign_role(
            self.OWNER_ID, self.EXP_ID, self.VIEWER_ID,
            rights_manager.ROLE_VIEWER)
        rights_manager.assign_role(
            self.OWNER_ID, self.EXP_ID, self.EDITOR_ID,
            rights_manager.ROLE_EDITOR)

        # Check that owner and editor may edit, but not viewer.
        summary = summary_services.get_exploration_summary_by_id(self.EXP_ID)
        self.assertTrue(summary.is_editable_by(self.OWNER_ID))
        self.assertTrue(summary.is_editable_by(self.EDITOR_ID))
        self.assertFalse(summary.is_editable_by(self.VIEWER_ID))

    def test_save_and_retrieve_exploration_summary(self):
        exploration = self.save_new_default_exploration(
            self.EXP_ID, self.OWNER_ID)
        exploration.param_specs = {
            'theParameter': param_domain.ParamSpec('Int')}
        exp_services._save_exploration(self.OWNER_ID, exploration, '', [])

        # change title and category
        exp_services.update_exploration(
            self.OWNER_ID, self.EXP_ID, [{
                'cmd': 'edit_exploration_property',
                'property_name': 'title',
                'new_value': 'A new title'
            }, {
                'cmd': 'edit_exploration_property',
                'property_name': 'category',
                'new_value': 'A new category'
            }],
            'Change title and category')

        retrieved_summary = summary_services.get_exploration_summary_by_id(
            self.EXP_ID)

        self.assertEqual(retrieved_summary.title, 'A new title')
        self.assertEqual(retrieved_summary.category, 'A new category')

    def test_summaries_are_deleted_when_activities_are_soft_deleted(self):
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
        # The exploration shows up in queries.
        self.assertEqual(
            len(summary_services.get_at_least_editable_activity_summaries(
                self.OWNER_ID)), 1)

        exp_services.delete_exploration(self.OWNER_ID, self.EXP_ID)

        # The deleted exploration does not show up in any queries.
        self.assertEqual(
            summary_services.get_at_least_editable_activity_summaries(
                self.OWNER_ID), [])

        # And the exploration summary is deleted.
        self.assertNotIn(self.EXP_ID, [
            model.activity_id
            for model in activity_models.ActivitySummaryModel.get_all(
                include_deleted_entities=True)])

    def test_summaries_are_deleted_when_activities_are_hard_deleted(self):
        self.save_new_default_exploration(self.EXP_ID, self.OWNER_ID)
        # The exploration shows up in queries.
        self.assertEqual(
            len(summary_services.get_at_least_editable_activity_summaries(
                self.OWNER_ID)), 1)

        exp_services.delete_exploration(
            self.OWNER_ID, self.EXP_ID, force_deletion=True)

        # The deleted exploration does not show up in any queries.
        self.assertEqual(
            summary_services.get_at_least_editable_activity_summaries(
                self.OWNER_ID), [])

        # And the exploration summary is deleted.
        self.assertNotIn(self.EXP_ID, [
            model.activity_id
            for model in activity_models.ActivitySummaryModel.get_all(
                include_deleted_entities=True)])


class ActivitySummaryQueryTests(SummaryServicesUnitTests):
    """Test queries for activity summaries."""

    ALBERT_EMAIL = 'albert@example.com'
    BOB_EMAIL = 'bob@example.com'
    ALBERT_NAME = 'albert'
    BOB_NAME = 'bob'

    EXP_ID_1 = 'eid1'
    EXP_ID_2 = 'eid2'

    EXPECTED_VERSION_1 = 4
    EXPECTED_VERSION_2 = 2

    def setUp(self):
        """Populate the database of explorations and their summaries.

        The sequence of events is:
        - (1) Albert creates EXP_ID_1.
        - (2) Bob edits the title of EXP_ID_1.
        - (3) Albert creates EXP_ID_2.
        - (4) Albert edits the title of EXP_ID_1.
        - (5) Albert edits the title of EXP_ID_2.
        - (6) Bob reverts Albert's last edit to EXP_ID_1.
        - (7) Albert deletes EXP_ID_1.
        - Bob tries to publish EXP_ID_2, and is denied access.
        - (8) Albert publishes EXP_ID_2.
        """
        super(ActivitySummaryQueryTests, self).setUp()

        self.ALBERT_ID = self.get_user_id_from_email(self.ALBERT_EMAIL)
        self.BOB_ID = self.get_user_id_from_email(self.BOB_EMAIL)
        self.register_editor(self.ALBERT_EMAIL, username=self.ALBERT_NAME)
        self.register_editor(self.BOB_EMAIL, username=self.BOB_NAME)

        exploration_1 = self.save_new_valid_exploration(
            self.EXP_ID_1, self.ALBERT_ID)

        exploration_1.title = 'Exploration 1 title'
        exp_services._save_exploration(
            self.BOB_ID, exploration_1, 'Changed title.', [])

        exploration_2 = self.save_new_valid_exploration(
            self.EXP_ID_2, self.ALBERT_ID)

        exploration_1.title = 'Exploration 1 Albert title'
        exp_services._save_exploration(
            self.ALBERT_ID, exploration_1,
            'Changed title to Albert1 title.', [])

        exploration_2.title = 'Exploration 2 Albert title'
        exp_services._save_exploration(
            self.ALBERT_ID, exploration_2, 'Changed title to Albert2.', [])

        exp_services.revert_exploration(self.BOB_ID, self.EXP_ID_1, 3, 2)

        with self.assertRaisesRegexp(
                Exception, 'This exploration cannot be published'):
            rights_manager.publish_exploration(self.BOB_ID, self.EXP_ID_2)

        rights_manager.publish_exploration(self.ALBERT_ID, self.EXP_ID_2)

    def _assert_summaries_are_equal(
            self, actual_summaries, expected_summaries):
        self.assertEqual(len(actual_summaries), len(expected_summaries))
        sorted_actual_summaries = sorted(
            actual_summaries,
            key=lambda x: '%s:%s' % (x.activity_type, x.id))
        sorted_expected_summaries = sorted(
            expected_summaries,
            key=lambda x: '%s:%s' % (x.activity_type, x.id))

        SIMPLE_PROPS = [
            'activity_type', 'id', 'title', 'category', 'objective',
            'language_code', 'skill_tags', 'status', 'community_owned',
            'owner_ids', 'editor_ids', 'viewer_ids', 'version',
            'activity_model_created_on', 'activity_model_last_updated']

        for ind in range(len(sorted_actual_summaries)):
            for prop in SIMPLE_PROPS:
                self.assertEqual(getattr(sorted_actual_summaries[ind], prop),
                                 getattr(sorted_expected_summaries[ind], prop))

    def test_get_non_private_activity_summaries(self):
        actual_summaries = (
            summary_services.get_non_private_activity_summaries())

        expected_summaries = [exp_domain.ActivitySummary(
            feconf.ACTIVITY_TYPE_EXPLORATION, self.EXP_ID_2,
            'Exploration 2 Albert title', 'A category', 'An objective', 'en',
            [], feconf.ACTIVITY_STATUS_PUBLIC, False,
            [self.ALBERT_ID], [], [], self.EXPECTED_VERSION_2,
            actual_summaries[0].activity_model_created_on,
            actual_summaries[0].activity_model_last_updated
        )]

        self._assert_summaries_are_equal(actual_summaries, expected_summaries)

    def test_get_all_activity_summaries(self):
        actual_summaries = summary_services.get_all_activity_summaries()

        expected_summaries = [exp_domain.ActivitySummary(
            feconf.ACTIVITY_TYPE_EXPLORATION, self.EXP_ID_1,
            'Exploration 1 title', 'A category', 'An objective', 'en', [],
            feconf.ACTIVITY_STATUS_PRIVATE, False, [self.ALBERT_ID], [], [],
            self.EXPECTED_VERSION_1,
            actual_summaries[0].activity_model_created_on,
            actual_summaries[0].activity_model_last_updated
        ), exp_domain.ActivitySummary(
            feconf.ACTIVITY_TYPE_EXPLORATION, self.EXP_ID_2,
            'Exploration 2 Albert title', 'A category', 'An objective', 'en',
            [], feconf.ACTIVITY_STATUS_PUBLIC, False, [self.ALBERT_ID], [], [],
            self.EXPECTED_VERSION_2,
            actual_summaries[1].activity_model_created_on,
            actual_summaries[1].activity_model_last_updated
        )]

        self._assert_summaries_are_equal(actual_summaries, expected_summaries)

    def test_get_at_least_editable_activity_summaries(self):
        exp_services.delete_exploration(self.ALBERT_ID, self.EXP_ID_1)

        actual_summaries = (
            summary_services.get_at_least_editable_activity_summaries(
                self.ALBERT_ID))
        expected_summaries = [exp_domain.ActivitySummary(
            feconf.ACTIVITY_TYPE_EXPLORATION, self.EXP_ID_2,
            'Exploration 2 Albert title', 'A category', 'An objective', 'en',
            [], feconf.ACTIVITY_STATUS_PUBLIC, False, [self.ALBERT_ID], [], [],
            self.EXPECTED_VERSION_2,
            actual_summaries[0].activity_model_created_on,
            actual_summaries[0].activity_model_last_updated
        )]
        self._assert_summaries_are_equal(actual_summaries, expected_summaries)

        # do similar test for Bob
        actual_summaries = (
            summary_services.get_at_least_editable_activity_summaries(
                self.BOB_ID))
        expected_summaries = []
        self._assert_summaries_are_equal(actual_summaries, expected_summaries)
