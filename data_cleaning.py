import re

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
