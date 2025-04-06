import json
import os
from final_refactor import refactor_java_code
from blu import extract_summary_from_code, sentence_bleu, meteor_score, SmoothingFunction
import nltk
from tqdm import tqdm

# Ensure required NLTK data is downloaded
nltk.download('wordnet')
nltk.download('punkt')

def process_dataset(input_file, output_file, limit=200):
    """Process the dataset through the refactoring pipeline and save results."""
    print(f"Processing dataset from {input_file}...")
    
    # Load and process dataset
    processed_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f)):
            if i >= limit:
                break
                
            try:
                data = json.loads(line.strip())
                code = data.get("code", "")
                docstring = data.get("docstring", "")
                
                if not code or not docstring:
                    continue
                
                # Run code through refactoring pipeline
                print(f"\nProcessing code {i+1}...")
                refactored_code = refactor_java_code(code)
                
                # Extract generated summary from refactored code
                generated_summary = extract_summary_from_code(refactored_code)
                
                if generated_summary:
                    processed_data.append({
                        "original_code": code,
                        "refactored_code": refactored_code,
                        "docstring": docstring,
                        "generated_summary": generated_summary
                    })
                    print(f"Successfully processed code {i+1}")
                else:
                    print(f"Warning: No summary generated for code {i+1}")
                    
            except Exception as e:
                print(f"Error processing line {i+1}: {e}")
                continue
    
    # Save processed data
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in processed_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"\nProcessed {len(processed_data)} instances")
    return processed_data

def evaluate_summaries(processed_data):
    """Evaluate the generated summaries against docstrings."""
    print("\nEvaluating summaries...")
    
    bleu_scores = []
    meteor_scores = []
    
    for item in tqdm(processed_data):
        # Tokenize reference and generated summary
        reference_tokens = [nltk.word_tokenize(item['docstring'])]
        generated_tokens = nltk.word_tokenize(item['generated_summary'])
        
        # Calculate BLEU score
        bleu = sentence_bleu(reference_tokens, generated_tokens,
                           weights=(0.25, 0.25, 0.25, 0.25),
                           smoothing_function=SmoothingFunction().method4)
        bleu_scores.append(bleu)
        
        # Calculate METEOR score
        meteor = meteor_score(reference_tokens, generated_tokens)
        meteor_scores.append(meteor)
    
    # Calculate average scores
    avg_bleu = sum(bleu_scores) / len(bleu_scores)
    avg_meteor = sum(meteor_scores) / len(meteor_scores)
    
    # Find best examples
    best_bleu_idx = bleu_scores.index(max(bleu_scores))
    best_meteor_idx = meteor_scores.index(max(meteor_scores))
    
    print("\n===== Evaluation Results =====")
    print(f"Average BLEU Score: {avg_bleu:.4f}")
    print(f"Average METEOR Score: {avg_meteor:.4f}")
    
    print("\n===== Best BLEU Score Example =====")
    print(f"BLEU Score: {bleu_scores[best_bleu_idx]:.4f}")
    print("\nOriginal Code:")
    print(processed_data[best_bleu_idx]['original_code'])
    print("\nRefactored Code:")
    print(processed_data[best_bleu_idx]['refactored_code'])
    print("\nDocstring:")
    print(processed_data[best_bleu_idx]['docstring'])
    print("\nGenerated Summary:")
    print(processed_data[best_bleu_idx]['generated_summary'])
    
    print("\n===== Best METEOR Score Example =====")
    print(f"METEOR Score: {meteor_scores[best_meteor_idx]:.4f}")
    print("\nOriginal Code:")
    print(processed_data[best_meteor_idx]['original_code'])
    print("\nRefactored Code:")
    print(processed_data[best_meteor_idx]['refactored_code'])
    print("\nDocstring:")
    print(processed_data[best_meteor_idx]['docstring'])
    print("\nGenerated Summary:")
    print(processed_data[best_meteor_idx]['generated_summary'])

def main():
    # Input and output file paths
    input_file = "java dataset/test.jsonl"
    output_file = "java dataset/refactored_test.jsonl"
    
    # Process dataset
    processed_data = process_dataset(input_file, output_file)
    
    if processed_data:
        # Evaluate results
        evaluate_summaries(processed_data)
    else:
        print("No data was processed successfully. Please check the errors above.")

if __name__ == "__main__":
    main() 