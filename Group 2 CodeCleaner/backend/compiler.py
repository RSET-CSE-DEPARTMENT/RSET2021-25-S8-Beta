import subprocess
import os
import tempfile

def compile_and_run_java(code: str) -> dict:
    """
    Compiles and runs Java code, returning the output or error message.
    """
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the class name from the code
            class_name = None
            for line in code.split('\n'):
                if 'class' in line and '{' in line:
                    class_name = line.split('class')[1].split('{')[0].strip()
                    break
            
            if not class_name:
                return {
                    "status": "error",
                    "output": "No class definition found in the code."
                }

            # Create a Java file
            file_path = os.path.join(temp_dir, f"{class_name}.java")
            with open(file_path, 'w') as f:
                f.write(code)

            # Compile the Java file
            compile_process = subprocess.run(
                ['javac', file_path],
                capture_output=True,
                text=True
            )

            if compile_process.returncode != 0:
                return {
                    "status": "error",
                    "output": f"Compilation error:\n{compile_process.stderr}"
                }

            # Run the compiled Java program
            run_process = subprocess.run(
                ['java', '-cp', temp_dir, class_name],
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )

            if run_process.returncode != 0:
                return {
                    "status": "error",
                    "output": f"Runtime error:\n{run_process.stderr}"
                }

            return {
                "status": "success",
                "output": run_process.stdout
            }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "output": "Execution timed out (5 second limit)"
        }
    except Exception as e:
        return {
            "status": "error",
            "output": f"An error occurred: {str(e)}"
        } 