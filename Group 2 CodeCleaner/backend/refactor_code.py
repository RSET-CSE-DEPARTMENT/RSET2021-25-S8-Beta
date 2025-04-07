import re

def remove_unreachable_code(code):
    """Remove unreachable code blocks and dead code."""
    lines = code.split("\n")
    reachable_code = []
    is_reachable = True
    skip_block = False
    in_dead_zone = False

    for line in lines:
        stripped_line = line.strip()

        # Reset reachability when we hit a new block
        if stripped_line.endswith("{") and ("class " not in stripped_line):
            is_reachable = True
            in_dead_zone = False

        # Handle return statements
        if re.match(r"\breturn\b\s*[^;]*;", stripped_line):
            reachable_code.append(line)
            is_reachable = False
            in_dead_zone = True
            continue

        # Skip everything after a return until we hit a closing brace
        if in_dead_zone:
            if stripped_line == "}":
                reachable_code.append(line)
                in_dead_zone = False
            continue

        if not is_reachable:
            if stripped_line == "}":  
                reachable_code.append(line)  # Keep closing braces
            continue

        if re.match(r"if\s*\(false\)\s*{", stripped_line):
            skip_block = True
            continue

        if skip_block:
            if stripped_line == "}":
                skip_block = False
            continue

        if stripped_line == "}":
            reachable_code.append(line)
            continue

        if is_reachable:
            reachable_code.append(line)
    
    return "\n".join(reachable_code)

def count_variable_references(code):
    """Count references to variables in the code."""
    variable_pattern = r"\b(int|double|String|boolean|char|float|long|short|byte|int\[\]|double\[\]|String\[\]|boolean\[\]|char\[\]|float\[\]|long\[\]|short\[\]|byte\[\])\s+(\w+)(\s*=\s*[^;]*)?;"
    
    declaration_pattern = re.compile(variable_pattern)
    variable_names = []
    reference_counts = {}
    
    for match in declaration_pattern.finditer(code):
        variable_name = match.group(2)
        variable_names.append(variable_name)
        reference_counts[variable_name] = 0
    
    for variable in variable_names:
        reference_pattern = rf"\b{variable}\b"
        count = len(re.findall(reference_pattern, code)) - 1
        reference_counts[variable] = max(0, count)
    
    return reference_counts

def remove_unused_declarations(code, reference_counts):
    """Remove unused variable declarations."""
    lines = code.split("\n")
    modified_code = []
    
    variable_pattern = r"\b(int|double|String|boolean|char|float|long|short|byte|int\[\]|double\[\]|String\[\]|boolean\[\]|char\[\]|float\[\]|long\[\]|short\[\]|byte\[\])\s+(\w+)(\s*=\s*[^;]*)?;"
    declaration_pattern = re.compile(variable_pattern)
    
    for line in lines:
        match = declaration_pattern.match(line.strip())
        if match:
            variable_name = match.group(2)
            if reference_counts.get(variable_name, 1) == 0:
                continue
        modified_code.append(line)
    
    return "\n".join(modified_code)

def find_and_refactor_repeated_blocks(code, function_prefix="repeatedBlock"):
    """Find and refactor repeated code blocks into separate functions within the class."""
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    
    repeated_blocks = {}
    visited_lines = set()
    refactored_code = []
    function_definitions = []
    
    function_counter = 1
    
    assignment_pattern = re.compile(r"\b\w+\s*=.*")
    arithmetic_pattern = re.compile(r"\b\w+\s*([+\-*/%]=|\+\+|--).*")
    
    def has_balanced_braces(block):
        open_braces = sum(line.count("{") for line in block)
        close_braces = sum(line.count("}") for line in block)
        return open_braces == close_braces
    
    # Find the class definition and its body
    class_start = -1
    class_end = -1
    brace_count = 0
    
    for i, line in enumerate(lines):
        if "class" in line and "{" in line:
            class_start = i
            brace_count = 1
        elif class_start != -1:
            brace_count += line.count("{")
            brace_count -= line.count("}")
            if brace_count == 0:
                class_end = i + 1
                break
    
    if class_start == -1 or class_end == -1:
        return code  # Return original code if no class found
    
    # Process only the code inside the class
    class_body = lines[class_start:class_end]
    
    for i in range(len(class_body)):
        if i in visited_lines:
            continue

        for j in range(i + 1, len(class_body)):
            if j in visited_lines:
                continue
            
            block = []
            k = 0
            block_lines = set()
            
            while (i + k < len(class_body)) and (j + k < len(class_body)) and (class_body[i + k] == class_body[j + k]):
                if not (assignment_pattern.match(class_body[i + k]) or arithmetic_pattern.match(class_body[i + k])):
                    block.append(class_body[i + k])
                    block_lines.add(i + k)
                    block_lines.add(j + k)
                k += 1

            block_tuple = tuple(block)
            if len(block) > 1 and block_tuple not in repeated_blocks:
                if has_balanced_braces(block):
                    function_name = f"{function_prefix}{function_counter}"
                    repeated_blocks[block_tuple] = function_name
                    
                    function_definitions.append(
                        f"    private void {function_name}() {{\n" +
                        "\n".join([f"        {line}" for line in block]) +
                        "\n    }\n"
                    )
                    
                    visited_lines.update(block_lines)
                    function_counter += 1

            if block:
                break

    # Reconstruct the class with new functions
    result = []
    i = 0
    while i < len(class_body):
        replaced = False
        for block_tuple, function_name in repeated_blocks.items():
            block_size = len(block_tuple)

            if tuple(class_body[i:i + block_size]) == block_tuple:
                result.append(f"        {function_name}();")
                i += block_size
                replaced = True
                break
        
        if not replaced:
            result.append(class_body[i])
            i += 1

    # Insert new functions before the closing brace of the class
    if function_definitions:
        # Find the last closing brace of the class
        last_brace_index = -1
        for i, line in enumerate(result):
            if line.strip() == "}":
                last_brace_index = i
        
        if last_brace_index != -1:
            # Insert new functions before the closing brace
            result[last_brace_index:last_brace_index] = function_definitions

    # Reconstruct the full code
    return "\n".join(lines[:class_start] + result + lines[class_end:])

def clean_indentation(code, indent_size=4):
    """Clean and format code indentation."""
    lines = code.splitlines()
    clean_lines = []
    indent_level = 0
    indent_space = ' ' * indent_size
    
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            clean_lines.append('')
            continue
        if stripped_line.startswith('}') or stripped_line.startswith(']'):
            indent_level -= 1
        clean_lines.append(indent_space * indent_level + stripped_line)
        if stripped_line.endswith('{') or stripped_line.endswith('['):
            indent_level += 1
    
    return "\n".join(clean_lines)

def process_and_optimize_code(java_code):
    """Main function to process and optimize Java code."""
    # Step 1: Remove unreachable code
    java_code = remove_unreachable_code(java_code)
    
    # Step 2: Remove unused variable declarations
    reference_counts = count_variable_references(java_code)
    java_code = remove_unused_declarations(java_code, reference_counts)
    
    # Step 3: Refactor repeated blocks
    java_code = find_and_refactor_repeated_blocks(java_code)
    
    # Step 4: Clean indentation
    java_code = clean_indentation(java_code)
    
    return java_code
