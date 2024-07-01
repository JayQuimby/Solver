from ToT.Tree import ThoughtTree
from ToT.util import load_yaml

prompts = load_yaml('user', './ToT/prompts/')

instructions = prompts['INTRO']
user_prompt = prompts['START']
verify_answer = prompts['END']

def main():
    req = input(instructions + user_prompt)

    while req.strip() != '/exit':

        solver = ThoughtTree(req)
        
        answer = solver.solve()
        print(f'The bot has come up with the following answer:\n\n{answer}')

        affirm = input(verify_answer)
        
        if len(affirm) > 0 and affirm[0] == 'Y':
            req = input(user_prompt)
            
if __name__ == '__main__':
    main()


