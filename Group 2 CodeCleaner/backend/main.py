from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from refactor_code import process_and_optimize_code
from final_refactor import refactor_java_code, rename_variables, add_code_summaries
from comparison import compare_code_functionality
from compiler import compile_and_run_java

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request models
class CodeRequest(BaseModel):
    code: str
    optimization: bool = True
    renaming: bool = True
    summarization: bool = True

class ComparisonRequest(BaseModel):
    original_code: str
    cleaned_code: str

@app.get("/")
def read_root():
    return {"message": "CodeCleaner API is running!"}

@app.post("/process_code/")
def process_code(request: CodeRequest):
    processed_code = request.code
    steps_applied = []

    try:
        # Step 1: Code Optimization (if selected)
        if request.optimization:
            processed_code = process_and_optimize_code(processed_code)
            steps_applied.append("Refactoring")

        # Step 2: Variable Renaming (if selected)
        if request.renaming:
            processed_code = rename_variables(processed_code)
            steps_applied.append("Variable Renaming")

        # Step 3: Code Summarization (if selected)
        if request.summarization:
            processed_code = add_code_summaries(processed_code)
            steps_applied.append("Code Summarization")

        return {
            "processed_code": processed_code,
            "steps_applied": steps_applied
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare_code/")
def compare_code(request: ComparisonRequest):
    result = compare_code_functionality(request.original_code, request.cleaned_code)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["output"])
    return result

@app.post("/run_code/")
def run_code(request: CodeRequest):
    result = compile_and_run_java(request.code)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["output"])
    return result

# run backend first:  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# run frontend: npm run dev / npm start