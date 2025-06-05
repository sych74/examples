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
    def replacer(match):
        full = match.group(0)
        prefix = match.group(1)
        if prefix and any(p in prefix for p in ['baseUrl:', 'mixins:']):
            return full
        return re.sub(RAW_PATTERN, r"{globals.cdnUrl}/\1/\2@\3\4", full)

    content = re.sub(r"(^.*(?:baseUrl:|mixins:).*$|.*https://raw\.githubusercontent\.com/jelastic(?:-jps)?/[^ \n]+)", replacer, content, flags=re.MULTILINE)
    content = re.sub(r"(^.*(?:baseUrl:|mixins:).*$|.*https://github\.com/jelastic(?:-jps)?/[^ \n]+)", replacer, content, flags=re.MULTILINE)
    return content

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

    original = content
    content = replace_base_url(content)
    content = ensure_globals_cdn(content)
    content = replace_outside_blocks(content)
    content = hard_replace(content)

    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✔ Updated: {file_path}")

def walk_directory(root_dir):
    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            process_file(full_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursively update GitHub/raw URLs to CDN format.")
    parser.add_argument('-p', '--path', default='.', help='Root directory to start from')
    args = parser.parse_args()

    walk_directory(args.path)
