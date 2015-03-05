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

"""Domain object for statistics models."""

__author__ = 'Sean Lip'

import copy
import operator
import re
import sys
import utils

from core.platform import models
(stats_models,) = models.Registry.import_models([models.NAMES.statistics])


class StateRuleAnswerLog(object):
    """Domain object that stores answers which match different state rules.

    All methods and properties in this file should be independent of the
    specific storage model used.
    """
    def __init__(self, answers):
        # This dict represents a log of answers that hit this rule and that
        # have not been resolved. The keys of this dict are the answers encoded
        # as HTML strings, and the values are integer counts representing how
        # many times the answer has been entered.
        self.answers = copy.deepcopy(answers)

    @property
    def total_answer_count(self):
        """Total count of answers for this rule that have not been resolved."""
        # TODO(sll): Cache this computed property.
        total_count = 0
        for answer, count in self.answers.iteritems():
            total_count += count
        return total_count

    @classmethod
    def get_multi(cls, exploration_id, rule_data):
        """Gets domain objects corresponding to the given rule data.

        Args:
            exploration_id: the exploration id
            rule_data: a list of dicts, each with the following keys:
                (state_name, handler_name, rule_str).
        """
        # TODO(sll): Should each rule_str be unicode instead?
        answer_log_models = (
            stats_models.StateRuleAnswerLogModel.get_or_create_multi(
                exploration_id, rule_data))
        return [cls(answer_log_model.answers)
                for answer_log_model in answer_log_models]

    @classmethod
    def get(cls, exploration_id, state_name, handler_name, rule_str):
        # TODO(sll): Deprecate this method.
        return cls.get_multi(exploration_id, [{
            'state_name': state_name,
            'handler_name': handler_name,
            'rule_str': rule_str
        }])[0]

    def get_top_answers(self, N):
        """Returns the top N answers.

        Args:
            N: the maximum number of answers to return.

        Returns:
            A list of (answer, count) tuples for the N answers with the highest
            counts.
        """
        return sorted(
            self.answers.iteritems(), key=operator.itemgetter(1),
            reverse=True)[:N]

class StateAnswers(object):
    """Domain object that stores answers of states."""

    def __init__(self, exploration_id, exploration_version, state_name,
                 answers_list):
        """
        Initialize domain object for state answers.
        
        answers_list contains a list of answer dicts, each of which
        contains information about an answer, e.g. answer_string, session_id,
        time_taken_to_answer.
        """
        # TODO(msl): Store interaction type of this state, e.g. multiple choice
        self.exploration_id = exploration_id
        self.exploration_version = exploration_version
        self.state_name = state_name
        for answer in answers_list:
            StateAnswers.validate_answer(answer)
        self.answers_list = copy.deepcopy(answers_list)
        self.validate()

    def record_answer(self, exploration_id, exploration_version, state_name,
                      answer):
        StateAnswers.validate_answer(answer)
        self.answers_list.append(answer)

    def record_answers(self, exploration_id, exploration_version,
                       state_name, answers_list):
        for answer in answers_list:
            self.record_answer(
                exploration_id, exploration_version, state_name, answer)

    def save(self):
        state_answers_model = stats_models.StateAnswersModel.create_or_update(
            self.exploration_id, self.exploration_version, self.state_name,
            self.answers_list)
        state_answers_model.save()
            
    @classmethod
    def get(cls, exploration_id, exploration_version, state_name):
        """
        Get state answers domain object (this is obtained from 
        state_answers_model instance stored in data store).
        """
        state_answers_model = stats_models.StateAnswersModel.get_model(
            exploration_id, exploration_version, state_name)
        return cls(exploration_id, exploration_version, state_name,
                   answers_list=state_answers_model.answers_list)

    @classmethod
    def validate_answer(cls, answer_dict):
        # Minimum set of keys required for answer_dicts in answers_list
        REQUIRED_ANSWER_DICT_KEYS = ['answer_string', 'time_taken_to_answer',
                                     'session_id']

        # There is a danger of data overflow if the answer log exceeds
        # 1 MB. Given 1000-5000 answers, each answer must be at most
        # 200-1000 bytes in size. We will address this later if it
        # happens regularly. At the moment, a ValidationError is raised if
        # an answer exceeds the maximum size.
        MAX_BYTES_PER_ANSWER_STRING = 500
        
        # check type is dict
        if not isinstance(answer_dict, dict):
            raise utils.ValidationError(
                'Expected answer_dict to be a dict, received %s' %
                answer_dict)

        # check keys
        required_keys = set(REQUIRED_ANSWER_DICT_KEYS)
        actual_keys = set(answer_dict.keys())
        if not required_keys.issubset(actual_keys):
            # find missing keys
            missing_keys = required_keys.difference(actual_keys)
            raise utils.ValidationError(
                ('answer_dict misses required keys %s' % missing_keys))

        # check values of answer_dict
        if not isinstance(answer_dict['answer_string'], basestring):
            raise utils.ValidationError(
                'Expected answer_string to be a string, received %s' %
                answer_dict['answer_string'])

        if not (sys.getsizeof(answer_dict['answer_string']) <= 
                MAX_BYTES_PER_ANSWER_STRING):
            # TODO(msl): find a better way to deal with long answers,
            # e.g. just skip. At the moment, too long answers produce
            # a ValidationError.
            raise utils.ValidationError(
                'answer_string is too big to be stored: %s' %
                answer_dict['answer_string'])

        if not isinstance(answer_dict['session_id'], basestring):
            raise utils.ValidationError(
                'Expected session_id to be a string, received %s' %
                answer_dict['session_id'])

        if not isinstance(answer_dict['time_taken_to_answer'], float):
            raise utils.ValidationError(
                'Expected time_taken_to_answer to be a float, received %s' %
                answer_dict['time_taken_to_answer'])
    
    def validate(self):
        """Validates StateAnswers domain object entity.
        TODO(msl): validation should be done before committing to storage.

        In particular, check structure of answer dicts in answers_list:
           - Minimum set of keys: 'answer_string', 'time_taken_to_answer',
             'session_id'
           - Check length of every answer_string
           - Check time_taken_to_answer is positive
        """

        if not isinstance(self.exploration_id, basestring):
            raise utils.ValidationError(
                'Expected exploration_id to be a string, received %s' %
                self.exploration_id)
        
        if not isinstance(self.state_name, basestring):
            raise utils.ValidationError(
                'Expected state_name to be a string, received %s' %
                self.state_name)
        
        if not isinstance(self.answers_list, list):
            raise utils.ValidationError(
                'Expected answers_list to be a list, received %s' %
                self.answers_list)

        # Note: There is no need to validate content of answers_list here
        # because each answer is validated before it is appended to 
        # answers_list (which is faster than validating whole answers_list
        # each time a new answer is recorded).


class StateAnswersCalcOutput(object):
    """
    Domain object that stores output of calculations operating on
    state answers.
    """

    def __init__(self, exploration_id, exploration_version, state_name,
                 calculation_outputs):
        """
        Initialize domain object for state answers calculation output.

        calculation_outputs is a list of dicts; each dict represents a 
        visualization and contains the following keys: visualization_id,
        visualization_opts. visualization_opts contains the data to present,
        i.e. the calculation output in the format expected by the
        visualization, and e.g. title or axis labels.
        """
        self.exploration_id = exploration_id
        self.exploration_version = exploration_version
        self.state_name = state_name
        self.calculation_outputs = copy.deepcopy(calculation_outputs)
        self.validate()
        self.__commit_to_storage()

    def __commit_to_storage(self):
        stats_models.StateAnswersCalcOutputModel.create_or_update(
            self.exploration_id, self.exploration_version, self.state_name,
            self.calculation_outputs)

    def validate(self):
        """
        Validates StateAnswersCalcOutputModel domain object entity before
        it is commited to storage.

        In particular, check structure of visualization_opts in
        calculation_outputs.
        """

        # There is a danger of data overflow if answer_opts exceeds 1
        # MB. We will address this later if it happens regularly. At
        # the moment, a ValidationError is raised if an answer exceeds
        # the maximum size.
        MAX_BYTES_PER_VISUALIZATIONS_OPTS = 999999
        
        if not isinstance(self.exploration_id, basestring):
            raise utils.ValidationError(
                'Expected exploration_id to be a string, received %s' %
                self.exploration_id)
        
        if not isinstance(self.state_name, basestring):
            raise utils.ValidationError(
                'Expected state_name to be a string, received %s' %
                self.state_name)

        if not isinstance(self.calculation_outputs, list):
            raise utils.ValidationError(
                'Expected calculation_outputs to be a list, received %s' %
                self.calculation_outputs)

        for calc_output in self.calculation_outputs:
            if not isinstance(calc_output['visualization_id'], basestring):
                raise utils.ValidationError(
                    "Expected calc_output['visualization_id'] to be a string, received %s" %
                    self.calc_output['visualization_id'])
            visualization_opts = calc_output['visualization_opts']
            
            if not (sys.getsizeof(visualization_opts) <= 
                    MAX_BYTES_PER_VISUALIZATIONS_OPTS):
                # TODO(msl): find a better way to deal with big 
                # visualization_opts, e.g. just skip. At the moment,
                # too long answers produce a ValidationError.
                raise utils.ValidationError(
                    'visualization_opts is too big to be stored: %s' %
                    str(visualization_opts))

            # TODO(msl): check structure of visualization_opts

