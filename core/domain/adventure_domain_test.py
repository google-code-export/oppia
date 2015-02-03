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

"""Tests for adventure domain objects and methods defined on them."""

__author__ = 'Sean Lip'

from core.domain import adventure_domain
from core.tests import test_utils
import feconf
import utils


class AdventureDomainUnitTests(test_utils.GenericTestBase):
    """Test the adventure domain object."""

    def test_validation(self):
        """Test validation of adventures."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', '|||||TITLE|||||', '{{CATEGORY}}',
            objective=['objective', 'should', 'really', 'be', 'a', 'string'])

        with self.assertRaisesRegexp(
                utils.ValidationError, 'the adventure title'):
            adventure.validate()

        adventure.title = 'My Adventure'

        with self.assertRaisesRegexp(
                utils.ValidationError, 'the adventure category'):
            adventure.validate()

        adventure.category = 'Mathematics'

        with self.assertRaisesRegexp(
                utils.ValidationError, 'Expected objective to be a string'):
            adventure.validate()

        adventure.objective = 'learn how to do mathematics'

        adventure.language_code = 'fake_code'
        with self.assertRaisesRegexp(
                utils.ValidationError, 'Invalid language_code'):
            adventure.validate()
        adventure.language_code = 'English'
        with self.assertRaisesRegexp(
                utils.ValidationError, 'Invalid language_code'):
            adventure.validate()
        adventure.language_code = 'en'
        adventure.validate()

        self.assertEqual(adventure.entry_points, [])

        adventure.entry_points = [adventure_domain.EntryPoint.from_dict({
            'activity_type': feconf.ACTIVITY_TYPE_EXPLORATION,
            'activity_id': '123',
            'schema_version': 1,
        }), adventure_domain.EntryPoint.from_dict({
            'activity_type': feconf.ACTIVITY_TYPE_EXPLORATION,
            'activity_id': '123',
            'schema_version': 1,
        })]
        with self.assertRaisesRegexp(
                utils.ValidationError, 'entry points were duplicated'):
            adventure.validate()
        adventure.entry_points = [adventure_domain.EntryPoint.from_dict({
            'activity_type': feconf.ACTIVITY_TYPE_EXPLORATION,
            'activity_id': '123',
            'schema_version': 1,
        })]
        with self.assertRaisesRegexp(
                utils.ValidationError,
                'Could not find entry_point .* in the specification'):
            adventure.validate()

        adventure.add_activity(feconf.ACTIVITY_TYPE_EXPLORATION, '123')

        adventure.add_activity(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv_id_2')
        with self.assertRaisesRegexp(
                utils.ValidationError,
                'Adventures within an adventure are not currently supported.'):
            adventure.validate()
        adventure.delete_activity(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv_id_2')

        with self.assertRaisesRegexp(
                utils.ValidationError,
                'Could not find exploration with id 123'):
            adventure.validate()

        self.save_new_default_exploration('123', 'editor@example.com')
        adventure.validate()

    def test_update_title(self):
        """Test updating the title of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(adventure.title, 'Adventure Title')
        adventure.update_title('New Title')
        self.assertEqual(adventure.title, 'New Title')

    def test_update_category(self):
        """Test updating the category of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(adventure.category, 'Adventure Category')
        adventure.update_category('New Category')
        self.assertEqual(adventure.category, 'New Category')

    def test_update_objective(self):
        """Test updating the objective of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(adventure.objective, 'Adventure Objective')
        adventure.update_objective('New Objective')
        self.assertEqual(adventure.objective, 'New Objective')

    def test_update_language_code(self):
        """Test updating the language code of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(
            adventure.language_code, feconf.DEFAULT_LANGUAGE_CODE)
        adventure.update_language_code('pt')
        self.assertEqual(adventure.language_code, 'pt')

    def test_update_blurb(self):
        """Test updating the blurb of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(adventure.blurb, '')
        adventure.update_blurb('blurb')
        self.assertEqual(adventure.blurb, 'blurb')

    def test_update_entry_points(self):
        """Test updating the entry points of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')
        self.assertEqual(adventure.entry_points, [])

        adventure.add_entry_point(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1')
        self.assertEqual(len(adventure.entry_points), 1)
        self.assertEqual(
            adventure.entry_points[0].activity_type,
            feconf.ACTIVITY_TYPE_ADVENTURE)
        self.assertEqual(
            adventure.entry_points[0].activity_id, 'adv1')

        adventure.add_entry_point(feconf.ACTIVITY_TYPE_ADVENTURE, 'id2')
        adventure.add_entry_point(feconf.ACTIVITY_TYPE_EXPLORATION, 'id2')

        with self.assertRaisesRegexp(
                Exception, 'Entry point .* already exists.'):
            adventure.add_entry_point(feconf.ACTIVITY_TYPE_ADVENTURE, 'id2')

        self.assertEqual(len(adventure.entry_points), 3)
        self.assertEqual(
            adventure.entry_points[0].activity_type,
            feconf.ACTIVITY_TYPE_ADVENTURE)
        self.assertEqual(adventure.entry_points[0].activity_id, 'adv1')
        self.assertEqual(
            adventure.entry_points[1].activity_type,
            feconf.ACTIVITY_TYPE_ADVENTURE)
        self.assertEqual(adventure.entry_points[1].activity_id, 'id2')
        self.assertEqual(
            adventure.entry_points[2].activity_type,
            feconf.ACTIVITY_TYPE_EXPLORATION)
        self.assertEqual(adventure.entry_points[2].activity_id, 'id2')

        adventure.delete_entry_point(
            feconf.ACTIVITY_TYPE_EXPLORATION, 'fake_id', strict=False)
        self.assertEqual(len(adventure.entry_points), 3)
        with self.assertRaisesRegexp(
                Exception, 'Could not find entry point'):
            adventure.delete_entry_point(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'fake_id')

        with self.assertRaisesRegexp(
                Exception, 'Could not find entry point'):
            adventure.delete_entry_point(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'adv1')

        adventure.delete_entry_point(
            feconf.ACTIVITY_TYPE_ADVENTURE, 'id2')
        self.assertEqual(len(adventure.entry_points), 2)
        self.assertEqual(
            adventure.entry_points[0].activity_type,
            feconf.ACTIVITY_TYPE_ADVENTURE)
        self.assertEqual(adventure.entry_points[0].activity_id, 'adv1')
        self.assertEqual(
            adventure.entry_points[1].activity_type,
            feconf.ACTIVITY_TYPE_EXPLORATION)
        self.assertEqual(adventure.entry_points[1].activity_id, 'id2')

    def test_update_adventure_specification(self):
        """Test updating the specification of an adventure."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')

        adventure.add_activity(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp1')
        adventure.add_activity(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp2')
        adventure.add_activity(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1')

        adventure.add_entry_point(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp2')

        self.assertEqual(adventure.num_activities, 3)

        # Delete a fake activity
        with self.assertRaisesRegexp(
                Exception,
                'Could not find exploration id exp3 in adventure spec'):
            adventure.delete_activity(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'exp3')

        # Delete an activity that isn't an entry point
        adventure.delete_activity(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1')
        self.assertEqual(adventure.num_activities, 2)
        self.assertEqual(len(adventure.entry_points), 1)

        # Delete an activity that is an entry point
        adventure.delete_activity(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp2')
        self.assertEqual(adventure.num_activities, 1)
        self.assertEqual(adventure.entry_points, [])

    def test_update_and_validate_destination_specs(self):
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'Adventure Title', 'Adventure Category',
            'Adventure Objective')

        adventure.add_activity(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp1')
        exploration_spec = adventure.specification.exploration_specs['exp1']

        self.assertEqual(len(exploration_spec.destination_specs), 0)

        exploration_spec.update_destination_specs([
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'exp1',
                adventure_domain.DEST_DISPLAY_OPTION_ALWAYS)
        ])

        self.assertEqual(len(exploration_spec.destination_specs), 1)
        self.assertEqual(
            exploration_spec.destination_specs[0].activity_type,
            feconf.ACTIVITY_TYPE_EXPLORATION)
        self.assertEqual(
            exploration_spec.destination_specs[0].activity_id, 'exp1')
        self.assertEqual(
            exploration_spec.destination_specs[0].display_option,
            adventure_domain.DEST_DISPLAY_OPTION_ALWAYS)

        # Test validation.
        exploration_spec.validate()

        exploration_spec.update_destination_specs([
            adventure_domain.DestinationSpec(
                None, None, adventure_domain.DEST_DISPLAY_OPTION_ALWAYS)
        ])
        with self.assertRaisesRegexp(
                utils.ValidationError,
                'Expected activity type to be a string'):
            exploration_spec.validate()

        exploration_spec.update_destination_specs([
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1',
                'invalid_display_option')
        ])
        with self.assertRaisesRegexp(
                utils.ValidationError, 'Unrecognized display option'):
            exploration_spec.validate()

        exploration_spec.update_destination_specs([
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'same_dest',
                adventure_domain.DEST_DISPLAY_OPTION_ALWAYS),
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_EXPLORATION, 'same_dest',
                adventure_domain.DEST_DISPLAY_OPTION_ALWAYS),
        ])
        with self.assertRaisesRegexp(
                utils.ValidationError, 'Some destinations were duplicated'):
            exploration_spec.validate()

        exploration_spec.update_destination_specs([
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_EXPLORATION,
                'same_id_but_different_type',
                adventure_domain.DEST_DISPLAY_OPTION_ALWAYS),
            adventure_domain.DestinationSpec(
                feconf.ACTIVITY_TYPE_ADVENTURE,
                'same_id_but_different_type',
                adventure_domain.DEST_DISPLAY_OPTION_ALWAYS),
        ])
        exploration_spec.validate()


class AdventureConversionUnitTests(test_utils.GenericTestBase):
    """Test conversion methods on the adventure object."""

    def test_yaml_conversion(self):
        """Test conversion of adventures to YAML files and back again."""
        adventure = adventure_domain.Adventure.create_default(
            'adv_id', 'My Title', 'My Category', 'My Objective')
        adventure.add_activity(feconf.ACTIVITY_TYPE_EXPLORATION, 'exp1')
        adventure.add_activity(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1')
        adventure.add_entry_point(feconf.ACTIVITY_TYPE_ADVENTURE, 'adv1')

        adventure_yaml = adventure.to_yaml()
        reconstituted_adventure = adventure_domain.Adventure.from_yaml(
            'new_id', adventure_yaml)

        self.assertEqual(reconstituted_adventure.title, adventure.title)
        self.assertEqual(reconstituted_adventure.category, adventure.category)
        self.assertEqual(
            reconstituted_adventure.objective, adventure.objective)
        self.assertEqual(
            reconstituted_adventure.language_code, adventure.language_code)
        self.assertEqual(reconstituted_adventure.blurb, adventure.blurb)
        for ind in range(len(adventure.entry_points)):
            self.assertEqual(
                reconstituted_adventure.entry_points[ind].to_dict(),
                adventure.entry_points[ind].to_dict())
        self.assertEqual(
            reconstituted_adventure.specification.to_dict(),
            adventure.specification.to_dict())
