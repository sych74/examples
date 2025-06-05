sgi@MacBook-Pro-Henadii projects % cat convert_link.py
import os
import re
import yaml
import argparse

RAW_PATTERN = r"https://raw\.githubusercontent\.com/(jelastic(?:-jps)?)/([^/]+)/([^/]+)(/[^ \"'\n]*)?"
GITHUB_PATTERN = r"https://github\.com/(jelastic(?:-jps)?)/([^/]+)/blob/([^/]+)(/[^ \"'\n]*)?"
CDN_TEMPLATE = r"https://cdn.jsdelivr.net/gh/\1/\2@\3\4"
CDN_GLOBAL = "https://cdn.jsdelivr.net/gh"

def replace_base_url(content):
    pattern = re.compile(r"(baseUrl:\s*)(https://(?:raw\.githubusercontent\.com|github\.com)/(jelastic(?:-jps)?)/([^/]+)/([^/]+))")
    return pattern.sub(r"\1https://cdn.jsdelivr.net/gh/\3/\4@\5", content)

def ensure_globals_cdn(content):
    try:
        data = yaml.safe_load(content)
        if isinstance(data, dict) and "globals" in data:
            globals_block = data["globals"]
            if isinstance(globals_block, list) and CDN_GLOBAL not in globals_block:
                globals_block.insert(0, CDN_GLOBAL)
                return yaml.dump(data, sort_keys=False)
    except Exception:
        pass
    return content

def replace_outside_blocks(content):
    lines = content.splitlines()
    new_lines = []
    for line in lines:
        if 'baseUrl:' in line or 'mixins:' in line:
            new_lines.append(line)
            continue
        line = re.sub(RAW_PATTERN, CDN_TEMPLATE, line)
        line = re.sub(GITHUB_PATTERN, CDN_TEMPLATE, line)
        new_lines.append(line)
    return '\n'.join(new_lines)

def hard_replace(content):
    content = re.sub(RAW_PATTERN, CDN_TEMPLATE, content)
    content = re.sub(GITHUB_PATTERN, CDN_TEMPLATE, content)
    return content

def is_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            f.read()
        return True
    except Exception:
        return False

def process_file(file_path):
    if not is_text_file(file_path):
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    had_trailing_newline = content.endswith('\n')

    original = content
    content = replace_base_url(content)
    content = ensure_globals_cdn(content)
    content = replace_outside_blocks(content)
    content = hard_replace(content)

    if had_trailing_newline and not content.endswith('\n'):
        content += '\n'

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✔ Updated: {file_path}")

def walk_directory(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '.git' in dirnames:
            dirnames.remove('.git')  # Исключаем .git
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            process_file(full_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively convert GitHub/raw links to jsDelivr CDN format.")
    parser.add_argument('-p', '--path', default='.', help='Path to root directory')
    args = parser.parse_args()

    walk_directory(args.path)
