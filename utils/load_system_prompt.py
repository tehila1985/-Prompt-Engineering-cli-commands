import os

def load_system_prompt(level=1):
    prompt_path = f'prompts/prompt{level}.md'
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
