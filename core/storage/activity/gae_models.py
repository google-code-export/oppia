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

"""Models for Oppia activities (explorations and adventures)."""

__author__ = 'Sean Lip'

import datetime

import core.storage.base_model.gae_models as base_models
import core.storage.user.gae_models as user_models
import feconf

from google.appengine.ext import ndb


class AdventureSnapshotMetadataModel(base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for an adventure snapshot."""
    pass


class AdventureSnapshotContentModel(base_models.BaseSnapshotContentModel):
    """Storage model for the content of an adventure snapshot."""
    pass


class AdventureRightsSnapshotMetadataModel(
        base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for an adventure rights snapshot."""
    pass


class AdventureRightsSnapshotContentModel(
        base_models.BaseSnapshotContentModel):
    """Storage model for the content of an adventure rights snapshot."""
    pass


class ExplorationSnapshotMetadataModel(base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for an exploration snapshot."""
    pass


class ExplorationSnapshotContentModel(base_models.BaseSnapshotContentModel):
    """Storage model for the content of an exploration snapshot."""
    pass


class ExplorationRightsSnapshotMetadataModel(
        base_models.BaseSnapshotMetadataModel):
    """Storage model for the metadata for an exploration rights snapshot."""
    pass


class ExplorationRightsSnapshotContentModel(
        base_models.BaseSnapshotContentModel):
    """Storage model for the content of an exploration rights snapshot."""
    pass


class _BaseActivityModel(base_models.VersionedModel):
    """Versioned storage model for an Oppia activity.

    This is an abstract base class for adventures and explorations.
    """
    ALLOW_REVERT = True

    # The title of the activity.
    title = ndb.StringProperty(required=True)
    # The category of the activity (displayed in the gallery).
    category = ndb.StringProperty(required=True, indexed=True)
    # The objective of this activity.
    objective = ndb.TextProperty(default='', indexed=False)
    # The ISO 639-1 code for the language this activity is written in.
    language_code = ndb.StringProperty(
        default=feconf.DEFAULT_LANGUAGE_CODE, indexed=True)
    # A blurb for this activity.
    blurb = ndb.TextProperty(default='', indexed=False)

    @classmethod
    def get_new_id(cls, entity_name):
        """Overwrites the superclass method. Ensures that no exploration id
        conflicts with an adventure id.
        """
        return super(_BaseActivityModel, cls).get_new_id(
            entity_name,
            classes_to_avoid_collisions_with=[
                AdventureModel, ExplorationModel, _BaseActivityModel])


class AdventureModel(_BaseActivityModel):
    """Versioned storage model for an Oppia adventure."""
    SNAPSHOT_METADATA_CLASS = AdventureSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = AdventureSnapshotContentModel

    # The list of possible entry points for this adventure. Each entry point
    # is a dict with two keys: 'activity type' and 'activity id'.
    entry_points = ndb.JsonProperty(repeated=True, indexed=True)
    # A dict representing the specification of this adventure. It has keys
    # 'exploration_specs' and 'adventure_specs' whose values are dicts. The
    # keys of these subdicts are activity ids, and their values are dicts
    # representing ActivitySpecs (see adventure_domain.py for more details).
    specification = ndb.JsonProperty(default={}, indexed=False)

    def _trusted_commit(
            self, committer_id, commit_type, commit_message, commit_cmds):
        """Record the event to the commit log after the model commit.

        Note that this extends the superclass method.
        """
        super(AdventureModel, self)._trusted_commit(
            committer_id, commit_type, commit_message, commit_cmds)

        committer_user_settings_model = (
            user_models.UserSettingsModel.get_by_id(committer_id))
        committer_username = (
            committer_user_settings_model.username
            if committer_user_settings_model else '')

        rights = AdventureRightsModel.get_by_id(self.id)

        # TODO(msl): test if put_async() leads to any problems (make
        # sure summary dicts get updated correctly when adventures
        # are changed)
        AdventureCommitLogEntryModel(
            id=('adventure-%s-%s' % (self.id, self.version)),
            user_id=committer_id,
            username=committer_username,
            adventure_id=self.id,
            commit_type=commit_type,
            commit_message=commit_message,
            commit_cmds=commit_cmds,
            version=self.version,
            post_commit_status=rights.status,
            post_commit_community_owned=rights.community_owned,
            post_commit_is_private=(
                rights.status == feconf.ACTIVITY_STATUS_PRIVATE)
        ).put_async()


class ExplorationModel(_BaseActivityModel):
    """Versioned storage model for an Oppia exploration.

    This class should only be imported by the exploration domain file, the
    exploration services file, and the Exploration model test file.
    """
    SNAPSHOT_METADATA_CLASS = ExplorationSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = ExplorationSnapshotContentModel

    # Skill tags associated with this exploration.
    skill_tags = ndb.StringProperty(repeated=True, indexed=True)
    # 'Author notes' for this exploration.
    author_notes = ndb.TextProperty(default='', indexed=False)
    # The default HTML template to use for displaying the exploration to the
    # reader. This is a filename in data/skins (without the .html suffix).
    default_skin = ndb.StringProperty(default='conversation_v1')

    # The name of the initial state of this exploration.
    init_state_name = ndb.StringProperty(required=True, indexed=False)
    # A dict representing the states of this exploration. This dict should
    # not be empty.
    states = ndb.JsonProperty(default={}, indexed=False)
    # The dict of parameter specifications associated with this exploration.
    # Each specification is a dict whose keys are param names and whose values
    # are each dicts with a single key, 'obj_type', whose value is a string.
    param_specs = ndb.JsonProperty(default={}, indexed=False)
    # The list of parameter changes to be performed once at the start of a
    # reader's encounter with an exploration.
    param_changes = ndb.JsonProperty(repeated=True, indexed=False)

    @classmethod
    def get_exploration_count(cls):
        """Returns the total number of explorations."""
        return cls.get_all().count()

    def _trusted_commit(
            self, committer_id, commit_type, commit_message, commit_cmds):
        """Record the event to the commit log after the model commit.

        Note that this extends the superclass method.
        """
        super(ExplorationModel, self)._trusted_commit(
            committer_id, commit_type, commit_message, commit_cmds)

        committer_user_settings_model = (
            user_models.UserSettingsModel.get_by_id(committer_id))
        committer_username = (
            committer_user_settings_model.username
            if committer_user_settings_model else '')

        exp_rights = ExplorationRightsModel.get_by_id(self.id)

        # TODO(msl): test if put_async() leads to any problems (make
        # sure summary dicts get updated correctly when explorations
        # are changed)
        ExplorationCommitLogEntryModel(
            id=('exploration-%s-%s' % (self.id, self.version)),
            user_id=committer_id,
            username=committer_username,
            exploration_id=self.id,
            commit_type=commit_type,
            commit_message=commit_message,
            commit_cmds=commit_cmds,
            version=self.version,
            post_commit_status=exp_rights.status,
            post_commit_community_owned=exp_rights.community_owned,
            post_commit_is_private=(
                exp_rights.status == feconf.ACTIVITY_STATUS_PRIVATE)
        ).put_async()


class _BaseActivityRightsModel(base_models.VersionedModel):
    """Storage model for rights related to an activity.

    The id of each instance is the id of the corresponding activity.
    """
    ALLOW_REVERT = False

    # The user_ids of owners of this activity.
    owner_ids = ndb.StringProperty(indexed=True, repeated=True)
    # The user_ids of users who are allowed to edit this activity.
    editor_ids = ndb.StringProperty(indexed=True, repeated=True)
    # The user_ids of users who are allowed to view this activity.
    viewer_ids = ndb.StringProperty(indexed=True, repeated=True)

    # Whether this activity is editable by the community.
    community_owned = ndb.BooleanProperty(indexed=True, default=False)
    # For private activities, whether this exploration can be viewed
    # by anyone who has the URL. If the activity is not private, this
    # setting is ignored.
    viewable_if_private = ndb.BooleanProperty(indexed=True, default=False)

    # The publication status of this activity.
    status = ndb.StringProperty(
        default=feconf.ACTIVITY_STATUS_PRIVATE, indexed=True,
        choices=[
            feconf.ACTIVITY_STATUS_PRIVATE,
            feconf.ACTIVITY_STATUS_PUBLIC,
            feconf.ACTIVITY_STATUS_PUBLICIZED
        ]
    )


class AdventureRightsModel(_BaseActivityRightsModel):
    """Storage model for rights related to an adventure."""
    SNAPSHOT_METADATA_CLASS = AdventureRightsSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = AdventureRightsSnapshotContentModel

    def _trusted_commit(
            self, committer_id, commit_type, commit_message, commit_cmds):
        """Record the event to the commit log after the model commit.

        Note that this overrides the superclass method.
        """
        super(AdventureRightsModel, self)._trusted_commit(
            committer_id, commit_type, commit_message, commit_cmds)

        # Create and delete events will already be recorded in the
        # AdventureModel.
        if commit_type not in ['create', 'delete']:
            committer_user_settings_model = (
                user_models.UserSettingsModel.get_by_id(committer_id))
            committer_username = (
                committer_user_settings_model.username
                if committer_user_settings_model else '')
            # TODO(msl): test if put_async() leads to any problems (make
            # sure summary dicts get updated correctly when explorations
            # are changed)
            AdventureCommitLogEntryModel(
                id=('rights-%s-%s' % (self.id, self.version)),
                user_id=committer_id,
                username=committer_username,
                adventure_id=self.id,
                commit_type=commit_type,
                commit_message=commit_message,
                commit_cmds=commit_cmds,
                version=None,
                post_commit_status=self.status,
                post_commit_community_owned=self.community_owned,
                post_commit_is_private=(
                    self.status == feconf.ACTIVITY_STATUS_PRIVATE)
            ).put_async()


class ExplorationRightsModel(_BaseActivityRightsModel):
    """Storage model for rights related to an exploration."""
    SNAPSHOT_METADATA_CLASS = ExplorationRightsSnapshotMetadataModel
    SNAPSHOT_CONTENT_CLASS = ExplorationRightsSnapshotContentModel

    # The exploration id which this exploration was cloned from. If None, this
    # exploration was created from scratch.
    cloned_from = ndb.StringProperty()

    def _trusted_commit(
            self, committer_id, commit_type, commit_message, commit_cmds):
        """Record the event to the commit log after the model commit.

        Note that this overrides the superclass method.
        """
        super(ExplorationRightsModel, self)._trusted_commit(
            committer_id, commit_type, commit_message, commit_cmds)

        # Create and delete events will already be recorded in the
        # ExplorationModel.
        if commit_type not in ['create', 'delete']:
            committer_user_settings_model = (
                user_models.UserSettingsModel.get_by_id(committer_id))
            committer_username = (
                committer_user_settings_model.username
                if committer_user_settings_model else '')
            # TODO(msl): test if put_async() leads to any problems (make
            # sure summary dicts get updated correctly when explorations
            # are changed)
            ExplorationCommitLogEntryModel(
                id=('rights-%s-%s' % (self.id, self.version)),
                user_id=committer_id,
                username=committer_username,
                exploration_id=self.id,
                commit_type=commit_type,
                commit_message=commit_message,
                commit_cmds=commit_cmds,
                version=None,
                post_commit_status=self.status,
                post_commit_community_owned=self.community_owned,
                post_commit_is_private=(
                    self.status == feconf.ACTIVITY_STATUS_PRIVATE)
            ).put_async()


class _BaseCommitLogEntryModel(base_models.BaseModel):
    """Log of commits to activities.

    A new instance of this model is created and saved every time a commit to
    an activity model or an activity-rights model occurs.
    """
    # Update superclass model to make these properties indexed.
    created_on = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    last_updated = ndb.DateTimeProperty(auto_now=True, indexed=True)

    # The id of the user.
    user_id = ndb.StringProperty(indexed=True, required=True)
    # The username of the user, at the time of the edit.
    username = ndb.StringProperty(indexed=True, required=True)
    # The type of the commit: 'create', 'revert', 'edit', 'delete'.
    commit_type = ndb.StringProperty(indexed=True, required=True)
    # The commit message.
    commit_message = ndb.TextProperty(indexed=False)
    # The commit_cmds dict for this commit.
    commit_cmds = ndb.JsonProperty(indexed=False, required=True)
    # The version number of the activity after this commit. Only populated
    # for commits to the activity itself (as opposed to its rights, etc.)
    version = ndb.IntegerProperty()

    # The status of the activity after the edit event.
    post_commit_status = ndb.StringProperty(
        indexed=True,
        required=True,
        choices=[
            feconf.ACTIVITY_STATUS_PRIVATE,
            feconf.ACTIVITY_STATUS_PUBLIC,
            feconf.ACTIVITY_STATUS_PUBLICIZED,
        ]
    )
    # Whether the activity is community-owned after the edit event.
    post_commit_community_owned = ndb.BooleanProperty(indexed=True)
    # Whether the activity is private after the edit event. Having a separate
    # field for this makes queries faster, since an equality query on this
    # property is faster than an inequality query on post_commit_status.
    post_commit_is_private = ndb.BooleanProperty(indexed=True)

    @classmethod
    def get_commit(cls, exploration_id, version):
        raise NotImplementedError

    @classmethod
    def get_all_commits(cls, page_size, urlsafe_start_cursor):
        return cls._fetch_page_sorted_by_last_updated(
            cls.query(), page_size, urlsafe_start_cursor)

    @classmethod
    def get_all_non_private_commits(
            cls, page_size, urlsafe_start_cursor, max_age=None):
        if not isinstance(max_age, datetime.timedelta) and max_age is not None:
            raise ValueError(
                'max_age must be a datetime.timedelta instance or None.')

        query = cls.query(cls.post_commit_is_private == False)
        if max_age:
            query = query.filter(
                cls.last_updated >= datetime.datetime.utcnow() - max_age)
        return cls._fetch_page_sorted_by_last_updated(
            query, page_size, urlsafe_start_cursor)


class AdventureCommitLogEntryModel(_BaseCommitLogEntryModel):
    """Log of commits to adventures. A new instance of this model is created
    and saved every time a commit to AdventureModel or AdventureRightsModel
    occurs.

    The id for this model is of the form
    'adventure-{{ADV_ID}}-{{ADV_VERSION}}'.
    """
    # The id of the adventure being edited.
    adventure_id = ndb.StringProperty(indexed=True, required=True)

    @classmethod
    def get_commit(cls, exploration_id, version):
        return cls.get_by_id('exploration-%s-%s' % (exploration_id, version))


class ExplorationCommitLogEntryModel(_BaseCommitLogEntryModel):
    """Log of commits to explorations. A new instance of this model is created
    and saved every time a commit to ExplorationModel or ExplorationRightsModel
    occurs.

    The id for this model is of the form
    'exploration-{{EXP_ID}}-{{EXP_VERSION}}'.
    """
    # The id of the exploration being edited.
    exploration_id = ndb.StringProperty(indexed=True, required=True)

    @classmethod
    def get_commit(cls, exploration_id, version):
        return cls.get_by_id('exploration-%s-%s' % (exploration_id, version))


class ActivitySummaryModel(base_models.BaseModel):
    """Summary model for an Oppia activity.

    These are used in contexts where the content blob of the activity is not
    needed (e.g. the gallery).

    An ActivitySummaryModel instance stores the following information:

        id, activity_type (exploration, adventure), activity_id, title,
        category, objective, language_code, skill_tags, last_updated,
        created_on, status (private, public or publicized), community_owned,
        owner_ids, editor_ids, viewer_ids, version.

    The id of each ActivitySummaryModel instance is:
      - 'e:{{EXPLORATION_ID}}' for summaries corresponding to explorations
      - 'a:{{ADVENTURE_ID}}' for summaries corresponding to adventures
    """
    # The type of the activity.
    activity_type = ndb.StringProperty(required=True, choices=[
        feconf.ACTIVITY_TYPE_ADVENTURE,
        feconf.ACTIVITY_TYPE_EXPLORATION,
    ], indexed=True)
    # The id of the activity. This is different from the id of the
    # ActivitySummaryModel instance.
    activity_id = ndb.StringProperty(required=True, indexed=True)
    # The title of the activity.
    title = ndb.StringProperty(required=True, indexed=False)
    # The gallery category that the activity belongs to.
    category = ndb.StringProperty(required=True, indexed=True)
    # The objective of the activity.
    objective = ndb.TextProperty(required=True, indexed=False)
    # The ISO 639-1 code for the language this activity is written in.
    language_code = ndb.StringProperty(
        required=True, indexed=True)
    # Skill tags associated with this activity.
    skill_tags = ndb.StringProperty(repeated=True, indexed=True)

    # Time when the activity model was last updated (not to be
    # confused with the 'last_updated' field for this instance, which is the
    # time when the activity *summary* model was last updated).
    activity_model_last_updated = ndb.DateTimeProperty(indexed=True)
    # Time when the activity model was created (not to be confused
    # with the 'created_on' field for this instance, which is the time when the
    # activity *summary* model was created)
    activity_model_created_on = ndb.DateTimeProperty(indexed=True)

    # The publication status of this activity.
    status = ndb.StringProperty(
        default=feconf.ACTIVITY_STATUS_PRIVATE, indexed=True,
        choices=[
            feconf.ACTIVITY_STATUS_PRIVATE,
            feconf.ACTIVITY_STATUS_PUBLIC,
            feconf.ACTIVITY_STATUS_PUBLICIZED
        ]
    )

    # Whether this activity is owned by the community.
    community_owned = ndb.BooleanProperty(required=True, indexed=True)

    # The user_ids of owners of this activity.
    owner_ids = ndb.StringProperty(indexed=True, repeated=True)
    # The user_ids of users who are allowed to edit this activity.
    editor_ids = ndb.StringProperty(indexed=True, repeated=True)
    # The user_ids of users who are allowed to view this activity.
    viewer_ids = ndb.StringProperty(indexed=True, repeated=True)
    # The version number of the activity after this commit. Only populated
    # for commits to an activity (as opposed to its rights, etc.)
    version = ndb.IntegerProperty()

    _ACTIVITY_TYPE_TO_PREFIX = {
        feconf.ACTIVITY_TYPE_EXPLORATION: 'e',
        feconf.ACTIVITY_TYPE_ADVENTURE: 'a',
    }

    @classmethod
    def get_instance_id(cls, activity_type, activity_id):
        return '%s:%s' % (
            cls._ACTIVITY_TYPE_TO_PREFIX[activity_type],
            activity_id)

    @classmethod
    def get(cls, activity_type, activity_id):
        instance_id = cls.get_instance_id(activity_type, activity_id)
        return super(ActivitySummaryModel, cls).get(instance_id)

    @classmethod
    def get_non_private(cls):
        """Returns an iterable with non-private activity summary models."""
        return cls.query().filter(
            cls.status != feconf.ACTIVITY_STATUS_PRIVATE
        ).filter(
            cls.deleted == False
        ).fetch(feconf.DEFAULT_QUERY_LIMIT)

    @classmethod
    def get_at_least_editable(cls, user_id):
        """Returns an iterable with activity summaries that are at least
        editable by the given user.
        """
        return cls.query().filter(
            ndb.OR(cls.owner_ids == user_id, cls.editor_ids == user_id)
        ).filter(
            cls.deleted == False
        ).fetch(feconf.DEFAULT_QUERY_LIMIT)
