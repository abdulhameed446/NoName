import re

# Function to fix the invalid escape sequences
def fix_invalid_escape_sequences(content):
    # Fixing escape sequences like \/ and <\/ by converting to raw strings
    content = re.sub(r'(<[a-zA-Z]+.*?)\\([\/\.\_\-])', r'\1\\\2', content)
    content = re.sub(r'(<[a-zA-Z]+.*?)\\([a-zA-Z]+)', r'\1\\\\\2', content)
    content = re.sub(r'(<[a-zA-Z]+.*?)\\([\/\.\_\-]+)', r'\1\\\\\2', content)  # Handle \/ and <\/ specifically
    return content

# Function to fix the IndexError by adding a safe check for findall()
def fix_index_error(content):
    # Regex to add a check for empty list when using findall
    findall_usage = r'(\s+token\s*=\s*csrf_regex\.findall\([^)]*\))'
    fixed_content = re.sub(findall_usage, lambda m: m.group(0) + "\n" + ' ' * m.group(0).count(' ') + 'if not tokens:\n' + ' ' * m.group(0).count(' ') + '    print(\"CSRF token not found\")\n' + ' ' * m.group(0).count(' ') + '    token = None', content)
    return fixed_content

# Function to preserve indentation and fix minor issues
def fix_indentation(content):
    # Split the content into lines
    lines = content.splitlines()
    fixed_lines = []
    indent_level = None

    for line in lines:
        # Detect if the line starts with a certain indentation pattern
        stripped_line = line.lstrip()
        leading_spaces = len(line) - len(stripped_line)

        # Handle specific lines with indentation issues (e.g., 'if not tokens:')
        if stripped_line.startswith("if not tokens:"):
            fixed_lines.append(' ' * leading_spaces + 'if not tokens:')
            indent_level = leading_spaces + 4  # Ensure the block under the if statement is indented correctly
        else:
            # Maintain the same indentation level for other lines
            fixed_lines.append(' ' * leading_spaces + stripped_line)

    return '\n'.join(fixed_lines)

# Main function to read, fix, and write back to file
def main():
    # Path to the noname.py file
    file_path = 'noname.py'
    
    # Read the original file content
    with open(file_path, 'r') as file:
        content = file.read()

    # Apply the fixes
    content = fix_invalid_escape_sequences(content)
    content = fix_index_error(content)
    content = fix_indentation(content)

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.write(content)
    
    print("File has been fixed successfully.")

if __name__ == "__main__":
    main()
