from openai import OpenAI
import time
from datetime import datetime
import subprocess
import tempfile
import os

client = OpenAI() # Use your OpenAI API key here

def run_java_code(code, input_value):
    """Run Java code with given input and return output."""
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write the code to a file
            with open(os.path.join(temp_dir, "Test.java"), "w") as f:
                f.write(code)
            
            # Compile the code
            compile_result = subprocess.run(
                ["javac", os.path.join(temp_dir, "Test.java")],
                capture_output=True,
                text=True
            )
            
            if compile_result.returncode != 0:
                return f"Compilation error: {compile_result.stderr}"
            
            # Run the code with input
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, "Test"],
                input=str(input_value),
                capture_output=True,
                text=True
            )
            
            return run_result.stdout.strip()
    except Exception as e:
        return f"Error running code: {str(e)}"

def compare_code_functionality(original_code, cleaned_code):
    """
    Compares the functionality of original and cleaned code using both execution and OpenAI.
    Returns a tuple of (is_same_functionality: bool, explanation: str)
    """
    # Generate test inputs based on the code
    test_inputs = []
    
    # Check for different types of inputs based on code content
    if "int" in original_code:
        # For integer inputs, test with various values including edge cases
        test_inputs = [
            0,  # Edge case: zero
            1,  # Small positive
            -1, # Negative
            5,  # Medium positive
            10, # Larger positive
            100 # Large positive
        ]
    
    if "String" in original_code:
        # For String inputs, test with various cases
        test_inputs.extend([
            "",      # Empty string
            "test",  # Normal string
            "123",   # Numeric string
            " ",     # Space
            "null"   # null string
        ])
    
    if "double" in original_code or "float" in original_code:
        # For floating point inputs
        test_inputs.extend([
            0.0,    # Zero
            1.0,    # One
            -1.0,   # Negative
            0.5,    # Fraction
            10.5,   # Decimal
            100.0   # Large number
        ])
    
    if "boolean" in original_code:
        # For boolean inputs
        test_inputs.extend([True, False])
    
    # If no specific type found, use default test cases
    if not test_inputs:
        test_inputs = [1, 5, 10]
    
    # Run both codes with test inputs
    execution_results = []
    print("\n=== Code Execution Comparison ===")
    for input_value in test_inputs:
        print(f"\nTesting with input: {input_value}")
        original_output = run_java_code(original_code, input_value)
        cleaned_output = run_java_code(cleaned_code, input_value)
        
        # Compare outputs more thoroughly
        is_same = original_output == cleaned_output
        if not is_same:
            print(f"Output mismatch for input {input_value}:")
            print(f"Original: {original_output}")
            print(f"Cleaned: {cleaned_output}")
        
        execution_results.append({
            "input": input_value,
            "original_output": original_output,
            "cleaned_output": cleaned_output,
            "is_same": is_same
        })
    
    # Check if all outputs match
    all_outputs_match = all(result["is_same"] for result in execution_results)
    
    # OpenAI comparison with more specific instructions
    prompt = f"""
    You are a code functionality comparison expert. Your task is to analyze two versions of Java code and determine if they have the same core functionality.
    
    Guidelines for comparison:
    1. Focus on the actual behavior and output of the code
    2. Ignore differences in:
       - Variable/function/class names
       - Comments
       - Code formatting/style
       - Minor optimizations that don't change behavior
    3. Consider these as SAME functionality if:
       - Both codes produce the same output for the same inputs
       - Both codes handle the same use cases
       - Both codes maintain the same core logic/algorithms
       - Both codes handle edge cases similarly
    4. Consider these as DIFFERENT functionality if:
       - Output differs for same inputs
       - One handles edge cases that the other doesn't
       - Core logic or algorithm has been changed
       - Important functionality has been added/removed
       - One version is missing critical calculations
       - One version has different error handling

    Original Code:
    ```java
    {original_code}
    ```

    Cleaned Code:
    ```java
    {cleaned_code}
    ```

    Respond with ONLY one of these two lines:
    "SAME_FUNCTIONALITY: Both code versions maintain identical core behavior"
    "DIFFERENT_FUNCTIONALITY: Core behavior has been altered"
    """

    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            print(f"\nAttempt {attempt + 1}/{max_retries} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert in analyzing and comparing Java code functionality. Be precise and respond only with the exact format specified. Pay special attention to missing calculations or altered logic."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            response = completion.choices[0].message.content.strip()
            is_same = response.startswith("SAME_FUNCTIONALITY")
            
            print(f"Successfully got response: {response[:100]}...")
            
            # Only consider functionality the same if both AI and execution agree
            # AND there are no output mismatches
            final_is_same = is_same and all_outputs_match
            
            return {
                "output": response,
                "is_same_functionality": final_is_same,
                "explanation": response,  # Only return the AI response, not the execution details
                "status": "success"
            }

        except Exception as e:
            error_msg = str(e)
            print(f"\nError on attempt {attempt + 1}: {error_msg}")
            
            # Check for specific error types
            if "rate_limit_exceeded" in error_msg.lower():
                print("Rate limit exceeded. Waiting before retry...")
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            elif "insufficient_quota" in error_msg.lower():
                print("API quota exceeded. Please check your OpenAI account limits.")
                break
            elif "invalid_api_key" in error_msg.lower():
                print("Invalid API key. Please check your API key configuration.")
                break
            elif "context_length_exceeded" in error_msg.lower():
                print("Context length exceeded. Code might be too long.")
                break
            else:
                print(f"Unknown error: {error_msg}")
                time.sleep(retry_delay)  # Wait before retrying

    # If we get here, all retries failed
    error_msg = f"Failed after {max_retries} attempts. Last error: {error_msg}"
    print(f"\nFinal error: {error_msg}")
    return {
        "output": error_msg,
        "is_same_functionality": None,
        "explanation": error_msg,
        "status": "error"
    } 