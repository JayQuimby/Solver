from typing import List
from ToT.util import query_local_llm, load_yaml, extract_score

PROMPTS = {**load_yaml('model', './ToT/prompts/')}

class ThoughtNode:
    def __init__(self, thought, goal, parent=None) -> None:
        self.parent: ThoughtNode = parent
        self.thought: str = thought
        self.max_width: int = 5
        self.children: List[ThoughtNode] = []
        self.score(goal)

    def __str__(self) -> str:
        return f'''Node:\n\tScore: {self.score}\n\tThought: {self.thought}\n\tN_Child: {len(self.children)}\n\tHas_Parent: {self.parent != None}'''

    def get_thought_process(self) -> str:
        return self.thought if self.parent is None else self.thought_helper(2) + f'\nStep 1\n' + self.thought

    def thought_helper(self, depth: int) -> str:
        if self.parent is None:
            return self.thought  
        else:
            return self.thought_helper(depth + 1) + f'\nStep {depth}:\n' + self.thought

    def score(self, problem) -> None:
        prompt: str = PROMPTS['SCORE'].format(problem=problem, thoughts=self.get_thought_process())
        scores: list[float] = []
        for _ in range(3):
            response, _ = query_local_llm(prompt)
            sc = extract_score(response)
            scores.append(sc)
        self.score: float = sum(scores)/len(scores)

    def add_child(self, t: str, g:str) -> None:
        node = ThoughtNode(t, g, parent=self)
        self.children.append(node)

    def generate_children(self, problem) -> None:
        prompt: str = PROMPTS['THINK'].format(problem=problem, thoughts=self.get_thought_process())
        num_nodes = max(0, int(self.max_width * self.score)//10)

        for _ in range(num_nodes):
            cur_t, _ = query_local_llm(prompt)
            self.add_child(cur_t, problem)


class ThoughtTree:
    def __init__(self, problem, max_depth=3, beam_width=3) -> None:
        self.root = ThoughtNode(problem)
        self.max_depth = max_depth
        self.beam_width = beam_width
        self.starter = PROMPTS['START'].format(problem=problem)
