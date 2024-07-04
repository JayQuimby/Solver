from ToT.util import query_local_llm, load_yaml, extract_score

PROMPTS = {**load_yaml('model', './ToT/prompts/')}
SCORE_THRESH = 0.9

class Node:

    def __init__(self, content: str, parent=None) -> None:
        self.content: str = content
        self.parent: Node = parent
        self.child: Node = None
        self.eval_score: float = 0.0

    def score(self, goal) -> None:
        prompt = PROMPTS['SCORE'].format(problem=goal, thoughts=self.content)
        sc, _ = query_local_llm(prompt)
        self. eval_score = extract_score(sc)

    def get_thought_process(self) -> str:
        if self.parent is None:
            return self.content
        else:
            return self.parent.get_thought_process() + '\n\n' + self.content
        
    def generate_next(self, goal) -> None:
        prompt = PROMPTS['THINK'].format(problem=goal, thoughts=self.get_thought_process())
        res, _ = query_local_llm(prompt)
        child_node = Node(res, self)
        child_node.score(goal)
        self.child = child_node

class ThoughtChain:

    def __init__(self, goal: str) -> None:
        self.goal = goal
        self.lines: list[Node] = []

    def start_lines(self, num_lines=10) -> None:
        prompt = PROMPTS['START'].format(problem=self.goal)
        for _ in range(num_lines):
            res, _ = query_local_llm(prompt)
            new_node = Node(res)
            new_node.score(self.goal)
            self.lines.append(new_node)

    def grow(self) -> None:
        for line in self.lines:
            while line.child is not None:
                line = line.child
            line.generate_next(self.goal)

    def search(self, max_depth=5):
        for _ in range(max_depth):
            self.grow()



