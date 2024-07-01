import requests, re

def format_msg(msg): 
    if type(msg) is list:
        return [{"role": "user", "content": str(m)} for m in msg]
    else:
        return [{"role": "user", "content": str(msg)}]

def query_local_llm(msgs, limit=4000) -> tuple[str, float]:
    # Replace with your actual server address and port
    url = "http://0.0.0.0:11434/api/chat/"
    payload = {
        "model": 'llama3',
        "messages" : format_msg(msgs),
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": limit,
        }
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        generation_dict = dict(response.json())
        comp_tok = generation_dict.get('eval_count', 0)
        output = generation_dict['message']['content']
        return output, comp_tok 
    else:
        print(f"Error: {response.status_code}, {response.text}")


class ThoughtNode:

    def __init__(self, thought, goal, parent=None) -> None:
        self.parent = parent
        self.thought = thought
        self.children = []
        self.score = self.get_score(goal)

    @staticmethod
    def extract_score(response):
        pattern = r"Score:\s*(\d+(?:\.\d+)?)"
        matches = re.findall(pattern, response, re.MULTILINE)
        if matches:
            return float(matches[0])
        else:
            return 0.0

    def get_score(self, problem):
        prompt = f"Evaluate how promising this thought is for solving the problem '{problem}' on a scale of 0 to 10: '{self.thought}' Make sure your response is formatted as follows 'Score: [value 0-10]'"
        scores = []
        for _ in range(3):
            response, _ = query_local_llm(prompt)
            sc = self.extract_score(response)
            scores.append(sc)
        self.score = sum(scores)/len(scores)

    def add_child(self, t):
        node = ThoughtNode(t, self)
        self.children.append(node)
 
class ThoughtTree:

    def __init__(self, problem, max_depth=3, beam_width=3) -> None:
        self.root = ThoughtNode(problem)
        self.max_depth = max_depth
        self.beam_width = beam_width

    def generate_thoughts(self, node: ThoughtNode) -> ThoughtNode:
        prompt = f"Given the problem or previous thought: '{node.thought}', generate the possible next thought or step that will help achieve the goal."
        for _ in range(self.beam_width):
            response, _ = query_local_llm(prompt)
            thoughts = response.strip()
            node.add_child(thoughts)
        return node


def main():
    problem = input('Enter a Query: ')
    tree = ThoughtTree(problem)
    solution = tree.search()
    
    print("Problem:\n", problem, '\n')
    print("\nSolution path:")
    for i, thought in enumerate(solution):
        print(f"{i+1}:\n{thought}\n")

if __name__ == '__main__':
    main()