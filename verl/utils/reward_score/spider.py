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

def extract_solution(solution_str, method='strict', prompt=None):
    assert method in ['strict', 'flexible']

    # the solution_str starts with the prompt and the remaining is the solution
    if prompt is not None:
        return solution_str.lower().strip().split(prompt.lower())[1].strip().split(';')[0].strip()
    else:
        return solution_str.lower().strip()

def compute_score(solution_str, ground_truth, extra_info, method='strict', format_score=0., score=1.):
    """The scoring function for GSM8k.

    Reference: Trung, Luong, et al. "Reft: Reasoning with reinforced fine-tuning." Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2024.

    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    answer = extract_solution(solution_str=solution_str, method=method, prompt=extra_info.get('prompt', None))
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
        print(f'error, score is {e}##{answer}##{ground_truth}##{extra_info.get("prompt", None)}')
        return format_score
    

    
if __name__ == "__main__":
    solution_str = "SELECT a FROM table"
    ground_truth = "SELECT * FROM table"
    print(compute_score(solution_str, ground_truth))