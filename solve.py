from ToT.Tree import ThoughtTree

instructions = '''Instructions:
This is an enhanced LLM search and should only be used for complex problems that LLM's can't regularly solve.
If you would like to exit the program type "/exit" and the program will terminate.
'''

user_prompt = 'Please enter a problem for the bot to solve: '
verify_answer = 'Has the bot accurately and completely answered the request? [Y/N]: '

def main():
    print(instructions)
    req = input(user_prompt)
    while req.strip() != '/exit':
        solver = ThoughtTree(req)
        answer = solver.solve()

        print(f'The bot has come up with the following answer:\n\n{answer}')

        affirm = input(verify_answer)
        
        if len(affirm) > 0 and affirm[0] == 'Y':
            req = input(user_prompt)
            


if __name__ == '__main__':
    main()


