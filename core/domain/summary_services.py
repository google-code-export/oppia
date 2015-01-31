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

"""Commands that can be used to operate on activity summaries."""

__author__ = 'Sean Lip'

from core.domain import exp_domain
from core.platform import models
(activity_models,) = models.Registry.import_models([models.NAMES.activity])
import feconf
import utils


def get_summary_of_exploration(exploration):
    """Create ActivitySummary domain object for a given Exploration domain
    object and return it.
    """
    exp_rights = activity_models.ExplorationRightsModel.get_by_id(exploration.id)

    return exp_domain.ActivitySummary(
        feconf.ACTIVITY_TYPE_EXPLORATION,
        exploration.id,
        exploration.title,
        exploration.category,
        exploration.objective,
        exploration.language_code,
        exploration.skill_tags,
        exp_rights.status,
        exp_rights.community_owned,
        exp_rights.owner_ids,
        exp_rights.editor_ids,
        exp_rights.viewer_ids,
        exploration.version,
        exploration.created_on,
        exploration.last_updated)


def _get_activity_summary_from_model(model):
    """Given an ActivitySummaryModel instance, return the corresponding
    ActivitySummary domain object.
    """
    return exp_domain.ActivitySummary(
        model.activity_type, model.activity_id, model.title, model.category,
        model.objective, model.language_code, model.skill_tags,
        model.status, model.community_owned, model.owner_ids,
        model.editor_ids, model.viewer_ids, model.version,
        model.activity_model_created_on,
        model.activity_model_last_updated)


def _get_activity_summaries_from_models(activity_summary_models):
    """Given an iterable of ActivitySummaryModel instances, create a list
    containing the corresponding ActivitySummary domain objects.
    """
    return [
        _get_activity_summary_from_model(summary_model)
        for summary_model in activity_summary_models]


def get_activity_summaries_matching_query(query_string):
    """Returns a list with all activity summary domain objects matching the
    given search query string.
    """
    activity_ids, unused_cursor = search_explorations(query_string)
    summary_models = [
        model for model in activity_models.ActivitySummaryModel.get_multi(
            activity_ids)
        if model is not None]
    return _get_activity_summaries_from_models(summary_models)


def get_non_private_activity_summaries():
    """Returns a list with all non-private activity summary domain objects."""
    return _get_activity_summaries_from_models(
        activity_models.ActivitySummaryModel.get_non_private())


def get_all_activity_summaries():
    """Returns a list with all activity summary domain objects."""
    return _get_activity_summaries_from_models(
        activity_models.ActivitySummaryModel.get_all())


def get_at_least_editable_activity_summaries(user_id):
    """Returns a list with all activity summary domain objects that are
    at least editable by the given user.
    """
    return _get_activity_summaries_from_models(
        activity_models.ActivitySummaryModel.get_at_least_editable(
            user_id=user_id))


def get_exploration_summary_by_id(exploration_id):
    """Returns an ActivitySummary domain object corresponding to the
    exploration with the given exploration_id.
    """
    # TODO(msl): Maybe use memcache similarly to get_exploration_by_id.
    exp_summary_model = activity_models.ActivitySummaryModel.get(
        feconf.ACTIVITY_TYPE_EXPLORATION, exploration_id)
    if exp_summary_model:
        exp_summary = _get_activity_summary_from_model(
            exp_summary_model)
        assert exp_summary.activity_type == feconf.ACTIVITY_TYPE_EXPLORATION
        return exp_summary
    else:
        return None

