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

"""Domain objects for an adventure and its constituents.

Domain objects capture domain-specific logic and are agnostic of how the
objects they represent are stored. All methods and properties in this file
should therefore be independent of the specific storage models used."""

__author__ = 'Sean Lip'

from core.domain import activity_utils
import utils


class DestinationSpec(object):
    """Domain object for the specification of a destination to suggest at the
    end of a particular activity, together with conditions for offering the
    destination.

    A DestinationSpec has the following attributes:
      - activity_type: str. The type of the activity; this is either
          feconf.ACTIVITY_TYPE_EXPLORATION or feconf.ACTIVITY_TYPE_ADVENTURE.
      - activity_id: str. The id of the activity.
      - display_option: str. The calculation method for determining whether
          to show this destination. Currently takes only one value:
          _DEST_DISPLAY_OPTION_ALWAYS.
    """
    _CURRENT_DICT_SCHEMA_VERSION = 1

    # For reasons of backwards compatibility, the values of these constants
    # should not be changed.
    _DEST_DISPLAY_OPTION_ALWAYS = 'always'

    def __init__(self, activity_type, activity_id, display_option):
        self.activity_type = activity_type
        self.activity_id = activity_id
        self.display_option = display_option

    def validate(self):
        # Validate the activity type.
        if not isinstance(self.activity_type, basestring):
            raise utils.ValidationError(
                'Expected activity type to be a string, received %s'
                % self.activity_type)
        if self.activity_type not in [
                feconf.ACTIVITY_TYPE_EXPLORATION,
                feconf.ACTIVITY_TYPE_ADVENTURE]:
            raise utils.ValidationError(
                'Unrecognized activity type: %s' % self.activity_type)

        # Validate the activity id. This validation does not touch the
        # datastore, though -- if the id is not found then a 404 error arises.
        # TODO(sll): Write a continuously-running job that checks for this and
        # either hides adventures that have invalid destinations, or
        # automatically removes invalid destination specs.
        if not isinstance(self.activity_id, basestring):
            raise utils.ValidationError(
                'Expected activity id to be a string, received %s'
                % self.activity_id)

        # Validate the display option.
        if not isinstance(self.display_option, basestring):
            raise utils.ValidationError(
                'Expected display option to be a string, received %s'
                % self.display_option)
        if self.display_option not in [cls._DEST_DISPLAY_OPTION_ALWAYS]:
            raise utils.ValidationError(
                'Unrecognized display option: %s' % self.activity_type)

    @classmethod
    def from_dict(cls, destination_spec_dict):
        if (destination_spec_dict['schema_version'] ==
                cls._CURRENT_DICT_SCHEMA_VERSION):
            return cls(
                destination_spec_dict['activity_type'],
                destination_spec_dict['activity_id'],
                destination_spec_dict['display_option'])
        else:
            raise Exception(
                'Invalid destination specification dict: %s' %
                destination_spec_dict)

    def to_dict(self):
        return {
            'activity_type': self.activity_type,
            'activity_id': self.activity_id,
            'display_option': self.display_option,
            'schema_version': self._CURRENT_DICT_SCHEMA_VERSION,
        }


class ActivitySpec(object):
    """Domain object for the specification of an activity that is part of an
    adventure.

    An ActivitySpec has the following attributes:
      - destination_spec: list of DestinationSpecs. Each item in this list is
          a possible recommended destination that is shown to the learner when
          they complete the activity.
    """
    _CURRENT_DICT_SCHEMA_VERSION = 1

    def __init__(self, destination_specs):
        self.destination_specs = destination_specs

    def add_destination_spec(self, activity_type, activity_id, display_option):
        raise NotImplementedError

    def update_destination_spec(self, destination_spec_index):
        raise NotImplementedError

    def delete_destination_spec(self, destination_spec_index):
        raise NotImplementedError

    def validate(self):
        if not isinstance(self.destination_specs, list):
            raise utils.ValidationError(
                'Invalid destination_specs: %s' % self.destination_specs)

        for dest_spec in self.destination_specs:
            dest_spec.validate()

    @classmethod
    def from_dict(cls, activity_spec_dict):
        if (activity_spec_dict['schema_version'] ==
                cls._CURRENT_DICT_SCHEMA_VERSION):
            return cls(activity_spec_dict['destination_specs'])
        else:
            raise Exception(
                'Invalid activity specification dict: %s' %
                activity_spec_dict)

    def to_dict(self):
        return {
            'destination_specs': [
                DestinationSpec.to_dict(dest_spec)
                for dest_spec in self.destination_specs],
            'schema_version': self._CURRENT_DICT_SCHEMA_VERSION,
        }


class AdventureSpec(object):
    """Domain object for the specification of an adventure.

    An AdventureSpec has the following attributes:
      - exploration_specs: dict whose keys are exploration ids and whose
          corresponding values are ActivitySpecs.
      - adventure_specs: dict whose keys are adventure ids and whose
          corresponding values are ActivitySpecs.
    """
    _CURRENT_DICT_SCHEMA_VERSION = 1

    def __init__(self, exploration_specs, adventure_specs):
        self.exploration_specs = exploration_specs
        self.adventure_specs = adventure_specs

    @classmethod
    def from_dict(cls, specification_dict):
        if (specification_dict['schema_version'] ==
                cls._CURRENT_DICT_SCHEMA_VERSION):
            return cls({
                exp_id: ActivitySpec.from_dict(exp_spec_dict)
                for (exp_id, exp_spec_dict) in
                specification_dict['explorations'].iteritems()
            }, {
                adv_id: ActivitySpec.from_dict(adv_spec_dict)
                for (adv_id, adv_spec_dict) in
                specification_dict['adventures'].iteritems()
            })
        else:
            raise Exception(
                'Invalid adventure specification dict: %s' %
                specification_dict)

    def to_dict(self):
        return {
            'adventures': {
                adv_id: adv_dests.to_list() for
                (adv_id, adv_dests) in self.adventures.iteritems()
            },
            'explorations': {
                exp_id: exp_dests.to_list() for
                (exp_id, exp_dests) in self.explorations.iteritems()
            },
            'schema_version': self._CURRENT_DICT_SCHEMA_VERSION,
        }

    @classmethod
    def create_default(cls):
        return cls({}, {})

    @property
    def contains(self, activity_type, activity_id):
        """Returns True iff this specification includes the given activity."""
        if activity_type == feconf.ACTIVITY_TYPE_EXPLORATION:
            return activity_id in self.exploration_specs
        elif activity_type == feconf.ACTIVITY_TYPE_ADVENTURE:
            return activity_id in self.adventure_specs
        else:
            raise Exception('Unrecognized activity type: %s' % activity_type)

    def validate(self):
        # Validate the exploration_specs dict.
        if not isinstance(self.exploration_specs, dict):
            raise utils.ValidationError(
                'Expected exploration specs to be a dict, received %s'
                % self.exploration_specs)

        for exp_id in self.exploration_specs:
            if not isinstance(exp_id, basestring):
                raise utils.ValidationError(
                    'Expected keys of exploration_specs to be strings, '
                    'received %s' % exp_id)

        # Validate the adventure_specs dict.
        if not isinstance(self.adventure_specs, dict):
            raise utils.ValidationError(
                'Expected adventure specs to be a dict, received %s'
                % self.adventure_specs)

        for adv_id in self.adventure_specs:
            if not isinstance(adv_id, basestring):
                raise utils.ValidationError(
                    'Expected keys of adventure_specs to be strings, '
                    'received %s' % adv_id)


class EntryPointSpec(object):
    """Domain object for specifying an entry point for an adventure.

    An EntryPointSpec has the following attributes:
      - activity_type: str. The type of the activity; this is either
          feconf.ACTIVITY_TYPE_EXPLORATION or feconf.ACTIVITY_TYPE_ADVENTURE.
      - activity_id: str. The id of the activity.
    """
    _CURRENT_DICT_SCHEMA_VERSION = 1

    def __init__(self, activity_type, activity_id):
        self.activity_type = activity_type
        self.activity_id = activity_id

    def validate(self):
        # Validate the activity type.
        if not isinstance(self.activity_type, basestring):
            raise utils.ValidationError(
                'Expected activity type to be a string, received %s'
                % self.activity_type)
        if self.activity_type not in [
                feconf.ACTIVITY_TYPE_EXPLORATION,
                feconf.ACTIVITY_TYPE_ADVENTURE]:
            raise utils.ValidationError(
                'Unrecognized activity type: %s' % self.activity_type)

        # Validate the activity id. This validation does not touch the
        # datastore, though -- if the id is not found then a 404 error arises.
        # TODO(sll): Write a continuously-running job that checks for this and
        # either hides adventures that have invalid entry points, or
        # automatically removes invalid entry point specs.
        if not isinstance(self.activity_id, basestring):
            raise utils.ValidationError(
                'Expected activity id to be a string, received %s'
                % self.activity_id)

    @classmethod
    def from_dict(cls, entry_point_spec_dict):
        if (entry_point_spec_dict['schema_version'] ==
                cls._CURRENT_DICT_SCHEMA_VERSION):
            return cls(
                entry_point_spec_dict['activity_type'],
                entry_point_spec_dict['activity_id'])
        else:
            raise Exception(
                'Invalid entry point specification dict: %s' %
                entry_point_spec_dict)

    def to_dict(self):
        return {
            'activity_type': self.activity_type,
            'activity_id': self.activity_id,
            'schema_version': self._CURRENT_DICT_SCHEMA_VERSION,
        }


class Adventure(object):
    """Domain object for an Oppia adventure."""

    def __init__(self, adventure_id, title, category, objective,
                 language_code, blurb, entry_points_list, specification_dict,
                 version, created_on=None, last_updated=None):
        self.id = adventure_id
        self.title = title
        self.category = category
        self.objective = objective
        self.language_code = language_code
        self.blurb = blurb
        self.entry_points = [
            EntryPointSpec.from_dict(ep_dict) for
            ep_dict in entry_points_list]
        self.specification = AdventureSpec.from_dict(specification_dict)
        self.version = version
        self.created_on = created_on
        self.last_updated = last_updated

    @classmethod
    def create_default_adventure(
            cls, adventure_id, title, category, objective='',
            language_code=feconf.DEFAULT_LANGUAGE_CODE):
        return cls(
            exploration_id, title, category, objective, language_code, '',
            feconf.ACTIVITY_TYPE_EXPLORATION, None,
            Specification.create_default(), 0)

    def is_playable(self):
        """Whether this adventure has been fully specified and can be shown
        to learners.

        Note that this only does syntactic checks. It does not check whether
        the corresponding ids appear in the datastore, or whether the
        corresponding activities are valid and/or publicly viewable.
        """
        # TODO(sll): Implement the following checks:
        # - Check that at least one entry point is specified.
        # - Check that the graph of activities is directed and acyclic.
        # - Check that each activity is reachable from at least one entry
        #     point.
        # - Check that all destinations in the adventure specification are
        #     fully specified.
        return True

    def validate(self):
        """Validates the adventure before it is committed to storage."""
        # Check that the title, category, objective and blurb are valid.
        if not isinstance(self.title, basestring):
            raise utils.ValidationError(
                'Expected title to be a string, received %s' % self.title)
        activity_utils.require_valid_name(self.title, 'the adventure title')

        if not isinstance(self.category, basestring):
            raise utils.ValidationError(
                'Expected category to be a string, received %s'
                % self.category)
        activity_utils.require_valid_name(
            self.category, 'the adventure category')

        if not isinstance(self.objective, basestring):
            raise utils.ValidationError(
                'Expected objective to be a string, received %s' %
                self.objective)

        if not isinstance(self.blurb, basestring):
            raise utils.ValidationError(
                'Expected blurb to be a string, received %s' % self.blurb)

        # Check that the language code is valid.
        if not isinstance(self.language_code, basestring):
            raise utils.ValidationError(
                'Expected language_code to be a string, received %s' %
                self.language_code)
        if not any([self.language_code == lc['code']
                    for lc in feconf.ALL_LANGUAGE_CODES]):
            raise utils.ValidationError(
                'Invalid language_code: %s' % self.language_code)

        # Check that the list of entry points is valid.
        if not isinstance(self.entry_points, list):
            raise utils.ValidationError(
                'Expected entry_points to be a list, received %s' %
                self.entry_points)

        # Check that each entry point is unique.
        uniquified_entry_points = set([
            '%s:%s' % (ep.activity_type, ep.activity_id)
            for ep in self.entry_points])
        if len(uniquified_entry_points) < len(self.entry_points):
            raise utils.ValidationError(
                'Some entry points were duplicated. The full list of entry '
                'points supplied is %s' % self.entry_points)

        # Check that each entry point is valid.
        for entry_point in self.entry_points:
            if not isinstance(entry_point, EntryPointSpec):
                raise utils.ValidationError(
                    'Expected entry_points to be an EntryPointSpec, received '
                    '%s' % entry_point)
            entry_point.validate()

            # Check that each entry point corresponds to a valid entry in the
            # adventure's specification dict.
            if not self.specification.contains(
                    entry_point.activity_type,
                    entry_point.activity_id):
                raise utils.ValidationError(
                    'Could not find entry_point (%s, %s) in the specification '
                    'for adventure %s' % (
                        entry_point.activity_type, entry_point.activity_id,
                        self.id))

        # Check that the specification dict entries are valid.
        self.specification.validate()

    def update_title(self, title):
        self.title = title

    def update_category(self, category):
        self.category = category

    def update_objective(self, objective):
        self.objective = objective

    def update_language_code(self, language_code):
        self.language_code = language_code

    def update_blurb(self, blurb):
        self.blurb = blurb

    def update_entry_points(self, entry_points):
        raise NotImplementedError

    def add_activity(self, activity_type, activity_id):
        raise NotImplementedError

    def delete_activity(self, activity_type, activity_id):
        raise NotImplementedError

    # The current version of the adventure schema. If any backward-
    # incompatible changes are made to the exploration schema in the YAML
    # definitions, this version number must be changed and a migration process
    # put in place.
    _CURRENT_ADVENTURE_SCHEMA_VERSION = 1

    @classmethod
    def from_yaml(cls, adventure_id):
        """Creates and returns an adventure from a YAML text string.

        The client should ensure that the adventure_id does not duplicate ids
        of existing adventures.
        """
        try:
            adventure_dict = utils.dict_from_yaml(yaml_content)
        except Exception as e:
            raise Exception(
                'Please ensure that you are uploading a YAML text file. The '
                'YAML parser returned the following error: %s' % e)

        adventure_schema_version = adventure_dict.get('schema_version')
        if adventure_schema_version is None:
            raise Exception('Invalid YAML file: no schema version specified.')
        if not (1 <= adventure_schema_version
                <= cls._CURRENT_ADVENTURE_SCHEMA_VERSION):
            raise Exception(
                'Sorry, we can only process v1 YAML files at present.')

        adventure = cls(
            adventure_id, adventure_dict['title'], adventure_dict['category'],
            adventure_dict['objective'], adventure_dict['language_code'],
            adventure_dict['blurb'], adventure_dict['entry_points'],
            Specification.from_dict(adventure_dict['specification']),
            None)

        return adventure

    def to_yaml(self):
        return utils.yaml_from_dict({
            'blurb': self.blurb,
            'category': self.category,
            'entry_points': [
                EntryPointSpec.to_dict(entry_point)
                for entry_point in self.entry_points],
            'language_code': self.language_code,
            'objective': self.objective,
            'schema_version': self._CURRENT_ADVENTURE_SCHEMA_VERSION,
            'specification': Specification.to_dict(self.specification),
            'title': self.title,
        })
