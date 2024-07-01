from requests import post
from yaml import safe_load
from typing import Tuple
from re import findall, MULTILINE

def extract_score(response) -> float:
        pattern = r"Score:\s*(\d+(?:\.\d+)?)"
        matches = findall(pattern, response, MULTILINE)
        if matches:
            return float(matches[0])
        else:
            return 0.0

def load_yaml(name: str, BASE: str='./') -> dict[str, str]:
    '''
    Input:
        name: string with the name of the .yml file 
        BASE: the directory which stores the .yml file, Default "./"

    Returns:
        The contents of a yaml file as a dict
    '''

    with open(BASE + name + '.yml', 'r') as file:
        data = safe_load(file)
    return data


def format_msg(msg) -> list[dict[str, str]]:
    '''
    Input:
        msg: Can be a list of strings or a string

    Output:
        Formatted strings or list of strings into conversation structure for LLM processing.
        E.G. [{"role": "user", "content": msg[0]} , {"role": "user", "content": msg[1]}]
    '''

    if type(msg) is list:
        return [{"role": "user", "content": str(m)} for m in msg]
    else:
        return [{"role": "user", "content": str(msg)}]


def query_local_llm(msgs, limit=4000, model_name='llama3', port=11434) -> Tuple[str, float]:
    '''
    Input:
        msgs: A list of strings or a string that will be given to the LLM.
        limit: The max number of completion tokens before forced stop. Cannot exceed the context length.
        model_name: string name of the model to use for completion.
        port: The port number for ollama server, default is 11434
        
    Output:
        Query local model using ollama on localhost.
        This function does not stream it only returns the final completion.
        returns the completion and the number of tokens generated
    '''

    url = f"http://0.0.0.0:{port}/api/chat/"
    payload = {
        "model": model_name,
        "messages" : format_msg(msgs),
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": limit,
        }
    }

    response = post(url, json=payload)
    if response.status_code == 200:
        generation_dict = dict(response.json())
        comp_tok = generation_dict.get('eval_count', 0)
        output = generation_dict['message']['content']
        return output, comp_tok 
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return '', 0