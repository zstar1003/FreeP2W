"""
Fix get_area() method calls in pdf2docx for fitz.Rect compatibility
"""

import os
import re

def fix_get_area(file_path):
    """Replace .get_area() with .width * .height"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern 1: simple rect.get_area() -> rect.width * rect.height
    # But we need to be careful with the variable name
    # Match patterns like: bbox.get_area(), intersection.get_area(), rect.get_area()

    # We'll use a more sophisticated approach: find all occurrences and replace
    def replace_get_area(match):
        var_name = match.group(1)
        return f"({var_name}.width * {var_name}.height)"

    # Pattern: variable_name.get_area()
    content = re.sub(r'(\w+(?:\.\w+)*)\.get_area\(\)', replace_get_area, content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# Find all Python files in pdf2docx
pdf2docx_dir = 'pdf2docx'
fixed_files = []

for root, dirs, files in os.walk(pdf2docx_dir):
    for file in files:
        if file.endswith('.py'):
            file_path = os.path.join(root, file)
            if fix_get_area(file_path):
                fixed_files.append(file_path)
                print(f"Fixed: {file_path}")

print(f"\nTotal files fixed: {len(fixed_files)}")
