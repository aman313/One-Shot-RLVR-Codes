# Copyright 2024 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from sqlglot import diff, exp, parse_one

def sort_select_list(tree: exp.Expression) -> exp.Expression:
    """
    Sort the select list of the tree by the canonical SQL string
    """
    for sel in tree.find_all(exp.Select):
        sel.set(
            "expressions",
            # stable sort by canonical SQL string
            sorted(sel.expressions, key=lambda e: e.sql())
        )
    return tree

def extract_solution(solution_str, method='strict'):
    assert method in ['strict', 'flexible']

    # get last line of the solution_str
    return solution_str.strip().split('\n')[-1].strip()


def compute_score(solution_str, ground_truth, method='strict', format_score=0., score=1.):
    """The scoring function for GSM8k.

    Reference: Trung, Luong, et al. "Reft: Reasoning with reinforced fine-tuning." Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2024.

    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    answer = extract_solution(solution_str=solution_str, method=method)
    try:
        answer_tree = parse_one(answer)
        ground_truth_tree = parse_one(ground_truth)
        sorted_answer_tree = sort_select_list(answer_tree)
        sorted_ground_truth_tree = sort_select_list(ground_truth_tree)
        tree_diff = diff(sorted_answer_tree, sorted_ground_truth_tree, delta_only=True)
        if len(tree_diff) == 0:
            print(f'no diff, score is {score}')
            return score
        else:
            print(f'diff, score is {format_score}')
            return format_score
    except Exception as e:
        print(f'error, score is {e}##{answer}##{ground_truth}')
        return format_score
    

    
if __name__ == "__main__":
    solution_str = "SELECT a FROM table"
    ground_truth = "SELECT * FROM table"
    print(compute_score(solution_str, ground_truth))