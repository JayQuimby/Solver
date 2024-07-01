import requests

def format_msg(msg): 
    if type(msg) is list:
        return [{"role": "user", "content": str(m)} for m in msg]
    else:
        return [{"role": "user", "content": str(msg)}]

def query_local_llm(msgs, limit=4000, model_name='codestral') -> tuple[str, float]:
    # Replace with your actual server address and port
    url = "http://0.0.0.0:11434/api/chat/"
    payload = {
        "model": model_name,
        "messages" : format_msg(msgs),
        "stream": False,
        "options": {
            "temperature": 1,
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
        return '', 0