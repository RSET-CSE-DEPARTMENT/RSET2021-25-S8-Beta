from transformers import AutoModel, AutoTokenizer
#from openai import OpenAI
import ollama
import re

#client = OpenAI()
device = "cuda" 
checkpoint = "C:/Users/justi/Documents/Project/summaryt5" # Load T5-based model
tokenizer = AutoTokenizer.from_pretrained(checkpoint, trust_remote_code=True)
model = AutoModel.from_pretrained(checkpoint, trust_remote_code=True).to(device)

def extract_code_from_markdown(code_text,comm):
    """Helper function to extract code from markdown code blocks."""
    lines = code_text.split("\n")
    inside_code_block = False
    extracted_code = []

    for line in lines:
        if line.strip().startswith("```java") or line.strip().startswith("```Java"):
            inside_code_block = True
            continue
        elif line.strip().startswith("```"):
            inside_code_block = False
            continue
        if inside_code_block:            
            if comm==1:
                line = line.split("//")[0].rstrip()
            elif comm==2:
                if line.strip():  # Ignore empty lines
                    splitline = line.split(';', 1)  # Split at ';'
                    if len(splitline) > 1 and splitline[1].lstrip().startswith("//"):  # Check if part after ';' is a comment
                        line = splitline[0].rstrip() + ';'  # Keep only code
            line = line.replace("System.out.print(", "System.out.println(")
            line = re.sub(r"System\.out.*?begin[\s\S]*?\(", "System.out.println(", line)
            extracted_code.append(line)

    return "\n".join(extracted_code) if extracted_code else code_text

def rename_variables(java_code):
    """Step 1: Rename variables, functions, and classes to meaningful names."""
    prompt = f"""
    analyze provided Java code and it's variables
    1. rename only the Variables to short names based on their purpose. infer meaningful names from the code's context.
    2. Function names to describe their behavior.
    Here is the Java code:
    {java_code}
    Return only the updated code.
    """
    response = ollama.chat(model="deepseek-coder:6.7b", messages=[
    {"role": "system", "content": "You are an AI assistant that helps with programming tasks."},
    {"role": "user", "content": prompt} ])
    '''
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing and refactoring Java code."},
            {"role": "user", "content": prompt}
        ]
    )'''

    renamed_code = response['message']['content']
    return extract_code_from_markdown(renamed_code,1)

def add_code_summaries(java_code):
    """Step 2: Add summaries and comments to the code."""
    lines = java_code.split("\n")
    brcount = 0
    max_level = 0
    comments_dict = {}

    # First pass: find maximum nesting level
    for line in lines:
        brcount += line.count('{')
        brcount -= line.count('}')
        if brcount > max_level:
            max_level = brcount

    # Second pass: generate summaries for each block
    for level in range(max_level):
        brcount = 0
        temp = ""
        line_number = 0
        start = False

        for line in lines:
            line_number += 1
            brcount += line.count('{')
            
            if brcount >= level + 1:
                if not start:
                    current_line = line_number
                temp += line + "\n"
                start = True
            elif start:
                if temp.strip():
                    input_ids = tokenizer(temp, return_tensors="pt").input_ids.to(device)
                    generated_ids = model.generate(input_ids, max_length=20)
                    summary = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
                    
                    # Only add meaningful summaries
                    if not (summary.startswith("public static ") or 
                           summary.startswith("function ") or 
                           summary.strip().endswith(";")):
                        comments_dict[current_line] = summary
                
                temp = ""
                start = False
            
            brcount -= line.count('}')

        # Handle the last block if any
        if temp.strip():
            input_ids = tokenizer(temp, return_tensors="pt").input_ids.to(device)
            generated_ids = model.generate(input_ids, max_length=20)
            summary = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
            if not (summary.startswith("public static ") or 
                   summary.startswith("function ") or 
                   summary.strip().endswith(";")):
                comments_dict[1] = summary

    # Add comments to the code
    final_lines = []
    for i, line in enumerate(lines, 1):
        if i in comments_dict:
            final_lines.append(f"// {comments_dict[i]}")
        final_lines.append(line)

    final_code = "\n".join(final_lines)
    #return extract_code_from_markdown(final_code)


    # Final summary check and correction
    prompt = f"""
    given is a Java code with some comments. Analyze the existing comments.
    - If and ONLY IF the comments are completely inaccurate, slightly alter the existing comment to provide better meaning.
    - keep the altered comments short .
    - If it is vaguely accurate to what is being done in the code, do not alter it.
    The code is given below:
    {final_code}

    Return the updated code, and preserve the structure and indentation.
    """
    response = ollama.chat(model="deepseek-coder:6.7b", messages=[
    {"role": "system", "content": "You are an AI assistant that helps with programming tasks."},
    {"role": "user", "content": prompt}
])
    '''
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in analyzing and refactoring Java code."},
            {"role": "user", "content": prompt}
        ]
    )
    '''
    final_code = response['message']['content']
    #final_code = completion.choices[0].message.content
    return extract_code_from_markdown(final_code,2)

def refactor_java_code(java_code):
    """
    Full refactoring process that includes both renaming and summarization.
    This function is kept for backward compatibility.
    """
    renamed_code = rename_variables(java_code)
    return add_code_summaries(renamed_code)
