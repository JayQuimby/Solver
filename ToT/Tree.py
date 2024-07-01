import re
from typing import List
from ToT.util import query_local_llm

class ThoughtNode:
    def __init__(self, thought, goal, parent=None) -> None:
        self.parent: ThoughtNode = parent
        self.thought: str = thought
        self.width: int = 5
        self.children: List[ThoughtNode] = []
        self.score(goal)

    def __str__(self) -> str:
        return f'''Node:
    Score: {self.score}
    Thought: {self.thought}
    Children: {self.children}
    Parent: {self.parent}
    '''

    def get_thought_process(self) -> str:

        def thought_helper(node: ThoughtNode, depth: int) -> str:
            return node.thought if node.parent is None else thought_helper(depth + 1) + f'\nStep {depth}:\n' + node.thought
        
        return self.thought if self.parent is None else thought_helper(2) + f'\nStep 1\n' + self.thought

    

    @staticmethod
    def extract_score(response) -> float:
        pattern = r"Score:\s*(\d+(?:\.\d+)?)"
        matches = re.findall(pattern, response, re.MULTILINE)
        if matches:
            return float(matches[0])
        else:
            return 0.5

    def score(self, problem) -> None:
        prompt: str = f"Evaluate how promising this thought is for solving the problem '{problem}' on a scale of 0 to 10: '{self.thought}' Make sure your response is formatted as follows 'Score: [value 0-10]'"
        scores: list[float] = []
        for _ in range(3):
            response, _ = query_local_llm(prompt)
            sc = self.extract_score(response)
            scores.append(sc)
        self.score: float = sum(scores)/len(scores)

    def add_child(self, t: str, g:str) -> None:
        node = ThoughtNode(t, g, parent=self)
        self.children.append(node)

    def generate_children(self, problem) -> None:
        prompt = f'We are attempting to solve this problem "{problem}", and we currently have this partial solution "{self.get_thought_process()}". Given this information please generate the next step to solving the problem.'
        num_nodes = max(0, int(self.width * self.score)//10)

        for _ in range(num_nodes):
            cur_t, _ = query_local_llm(prompt)
            self.add_child(cur_t, problem)


class ThoughtTree:
    def __init__(self, problem, model='codestral', max_depth=3, beam_width=3) -> None:
        self.root = ThoughtNode(problem)
        self.max_depth = max_depth
        self.beam_width = beam_width

    def generate_thoughts(self, node: ThoughtNode) -> ThoughtNode:
        prompt = f"Given the problem or previous thought: '{node.thought}', generate the possible next thought or step that will help achieve the goal."
        for _ in range(self.beam_width):
            response, _ = query_local_llm(prompt)
            thoughts = response.strip()
            node.add_child(thoughts)