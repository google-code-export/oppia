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

"""Classes for calculations to get interaction answer views."""

__author__ = 'Marcel Schmittfull'

from collections import Counter
import copy
import os

from core.domain import stats_domain
import feconf
import schema_utils
import utils


## TODO(msl): write
# cf extensions/objects/models/objects.py, or see interactions 
# define BaseCalculation similar to BaseObject

class BaseCalculation(object):
    """Base calculation class.

    This is the superclass for all calculations used to generate interaction
    answer views.
    """

    # These values should be overridden in subclasses.
    name = ''
    description = ''
    allowed_input_interactions = []

    

class AnswerCounts(BaseCalculation):
    """Class for calculating answer counts."""

    name = 'Answer counts'
    description = 'Calculate answer counts for each answer option.'
    # TODO(msl): Implement. Not used at the moment.
    allowed_input_interactions = ['MultipleChoiceInput']

    @classmethod
    def calculate_from_StateAnswersEntity(cls, state_answers):
        """
        Directly calculate answer counts from a single StateAnswers entity,
        without using map reduce. Return list of pairs (answer_string, count).
        TODO(msl): return StateAnswersCalcOutputModel
        """

        assert isinstance(state_answers, stats_domain.StateAnswers)
        answer_strings = [answer_dict['answer_string'] for answer_dict 
                          in state_answers.answers_list]

        answer_counts_as_list_of_pairs = Counter(answer_strings).items()

        calc_outputs = []
        calc_outputs.append(
            {'visualization_id': 'values_and_counts_table',
             'visualization_opts': {'data': answer_counts_as_list_of_pairs,
                                    'title': 'Answer counts',
                                    'column_labels': ['Answer', 'Count']}
             })
        
        # get StateAnswersCalcOutput instance
        state_answers_calc_output = stats_domain.StateAnswersCalcOutput(
            state_answers.exploration_id, state_answers.exploration_version,
            state_answers.state_name, calc_outputs)
        
        return state_answers_calc_output

