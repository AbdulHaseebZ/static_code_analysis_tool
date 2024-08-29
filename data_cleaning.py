import re
import pickle
import os
def correct_brackets(data: str) -> str:
    data = data.replace('List()', '[]').replace('List(', '[').replace('Map(', '{').replace(')', '}').replace('->', ':')
    stack = []
    result = []

    for char in data:
        if char == '{' or char == '[':
            stack.append(char)
            result.append(char)
        elif char == '}' or char == ']':
            if stack:
                last_open = stack.pop()
                if (char == '}' and last_open == '[') or (char == ']' and last_open == '{'):
                    # Replace the wrong closing bracket with the correct one
                    result.append(']' if last_open == '[' else '}')
                else:
                    result.append(char)
            else:
                result.append(char)
        else:
            result.append(char)

    return ''.join(result)

def storing_data(code_path, dictionary):
    """Store code_path and dictionary in separate pickle files."""
    with open(r"H:\github\static_code_analysis_tool\path.pkl", 'wb') as f:
        pickle.dump(code_path, f)
    with open(r"H:\github\static_code_analysis_tool\dict_file.pkl", 'wb') as f:
        pickle.dump(dictionary, f)

def get_data():
    """Returns the stored python dictionary."""
    with open(r"H:\github\static_code_analysis_tool\dict_file.pkl", 'rb') as f:
        dictionary = pickle.load(f)
    return dictionary
    

