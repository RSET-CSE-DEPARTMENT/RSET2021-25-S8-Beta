import nltk
import json
import sacrebleu
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
import os
import re
from final_refactor import refactor_java_code

# Ensure all required NLTK data is downloaded
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw-1.4')  # Open Multilingual Wordnet

def extract_summary_from_code(code):
    """Extract the summary from the first line comment of the code."""
    # Look for a comment at the start of the code
    # Handle both single-line and multi-line comments
    comment_pattern = r'^\s*(?://|/\*)\s*(.*?)(?:\*/)?$'
    first_line = code.split('\n')[0].strip()
    match = re.match(comment_pattern, first_line)
    if match:
        return match.group(1).strip()
    return None

# Path to the JSONL file
jsonl_file = "java dataset/test.jsonl"

# Create a file to store summary comparisons
with open("summary_comparisons.txt", "w", encoding="utf-8") as f:
    f.write("=== Summary Comparisons ===\n\n")

# Load dataset (limited to first 200 lines)
dataset = []
with open(jsonl_file, 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if i >= 10:  # Stop after 200 lines
            break
        try:
            data = json.loads(line.strip())
            code = data.get("code", "")
            docstring = data.get("docstring", "")
            
            if not docstring:
                print(f"Warning: No docstring found in line {i+1}")
                continue

            # Run code through refactoring pipeline to get summary
            print(f"\nProcessing code {i+1}...")
            refactored_code = refactor_java_code(code)
            
            # Extract summary from refactored code
            generated_summary = extract_summary_from_code(refactored_code)
            if not generated_summary:
                print(f"Warning: No summary generated for code {i+1}")
                continue

            # Save the comparison to file
            with open("summary_comparisons.txt", "a", encoding="utf-8") as f:
                f.write(f"=== Instance {i+1} ===\n")
                f.write("\n\nReference Summary (Docstring):\n")
                f.write(docstring)
                f.write("\n\nGenerated Summary (Comment):\n")
                f.write(generated_summary)
                f.write("\n\n" + "="*50 + "\n\n")

            dataset.append({
                "code": code,
                "refactored_code": refactored_code,
                "reference": [docstring],
                "generated": generated_summary,
                "index": i  # Add index to track position
            })
            print(f"Successfully processed code {i+1}")
            
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse JSON in line {i+1}: {e}")
            continue
        except Exception as e:
            print(f"Warning: Error processing line {i+1}: {e}")
            continue

if not dataset:
    print("Error: No valid data was loaded from the file!")
    exit(1)

print(f"\nSuccessfully processed {len(dataset)} instances from the dataset...")

# Tokenize references and generated summaries
tokenized_dataset = []
for item in dataset:
    reference_tokens = [nltk.word_tokenize(ref) for ref in item['reference']]
    generated_tokens = nltk.word_tokenize(item['generated'])
    tokenized_dataset.append({'reference': reference_tokens, 'generated': generated_tokens})

# Initialize variables for highest values
highest_bleu = 0
highest_meteor = 0
highest_bleu_instance = None
highest_meteor_instance = None

# Compute BLEU and METEOR scores for each instance
bleu_scores = []
meteor_scores = []
for idx, item in enumerate(tokenized_dataset):
    reference_tokens = item['reference']
    generated_tokens = item['generated']

    # Sentence BLEU-4 score with smoothing
    bleu = sentence_bleu(reference_tokens, generated_tokens, 
                         weights=(0.25, 0.25, 0.25, 0.25), 
                         smoothing_function=SmoothingFunction().method4)
    bleu_scores.append(bleu)

    # METEOR score
    meteor = meteor_score(reference_tokens, generated_tokens)
    meteor_scores.append(meteor)

    # Track highest BLEU score
    if bleu > highest_bleu:
        highest_bleu = bleu
        highest_bleu_instance = dataset[idx]

    # Track highest METEOR score
    if meteor > highest_meteor:
        highest_meteor = meteor
        highest_meteor_instance = dataset[idx]

# Compute average BLEU and METEOR scores
avg_bleu = sum(bleu_scores) / len(bleu_scores)
avg_meteor = sum(meteor_scores) / len(meteor_scores)

# Compute Corpus BLEU Score using SacreBLEU
references = [[item["reference"][0] for item in dataset]]  # List of reference lists
hypotheses = [item["generated"] for item in dataset]  # List of generated summaries
corpus_bleu_score = sacrebleu.corpus_bleu(hypotheses, references).score

# Display results
for i in range(len(dataset)):
    print(f"\nInstance {i}:")
    print(f"  Sentence BLEU: {bleu_scores[i]:.4f}")
    print(f"  METEOR: {meteor_scores[i]:.4f}")

print("\n===== Overall Results =====")
print(f"Average Sentence BLEU: {avg_bleu:.4f}")
print(f"Corpus BLEU: {corpus_bleu_score:.4f}")
print(f"Average METEOR: {avg_meteor:.4f}")

# Display highest BLEU instance
if highest_bleu_instance:
    print("\n===== 🔥 HIGHEST BLEU SCORE =====")
    print(f"Highest BLEU Score: {highest_bleu:.4f}")
    print(f"Original Code:\n{highest_bleu_instance['code']}")
    print(f"\nRefactored Code:\n{highest_bleu_instance['refactored_code']}")
    print(f"\nReference Summary (Docstring):\n{highest_bleu_instance['reference'][0]}")
    print(f"\nGenerated Summary (Comment):\n{highest_bleu_instance['generated']}")

# Display highest METEOR instance
if highest_meteor_instance:
    print("\n===== 🔥 HIGHEST METEOR SCORE =====")
    print(f"Highest METEOR Score: {highest_meteor:.4f}")
    print(f"Original Code:\n{highest_meteor_instance['code']}")
    print(f"\nRefactored Code:\n{highest_meteor_instance['refactored_code']}")
    print(f"\nReference Summary (Docstring):\n{highest_meteor_instance['reference'][0]}")
    print(f"\nGenerated Summary (Comment):\n{highest_meteor_instance['generated']}")

# After computing all scores, add them to the summary file
with open("summary_comparisons.txt", "a", encoding="utf-8") as f:
    f.write("\n\n=== SCORES FOR EACH INSTANCE ===\n\n")
    for i in range(len(dataset)):
        f.write(f"Instance {i+1}:\n")
        f.write(f"  Sentence BLEU: {bleu_scores[i]:.4f}\n")
        f.write(f"  METEOR: {meteor_scores[i]:.4f}\n")
        f.write("\n" + "-"*30 + "\n\n")

    # Add overall results at the end
    f.write("\n\n=== OVERALL RESULTS ===\n\n")
    f.write(f"Average Sentence BLEU: {avg_bleu:.4f}\n")
    f.write(f"Corpus BLEU: {corpus_bleu_score:.4f}\n")
    f.write(f"Average METEOR: {avg_meteor:.4f}\n")
    f.write("\n" + "="*50 + "\n\n")

    # Add highest scoring instances
    if highest_bleu_instance:
        f.write("\n=== HIGHEST BLEU SCORE INSTANCE ===\n")
        f.write(f"Score: {highest_bleu:.4f}\n")
        f.write(f"Original Code:\n{highest_bleu_instance['code']}\n")
        f.write(f"\nRefactored Code:\n{highest_bleu_instance['refactored_code']}\n")
        f.write(f"\nReference Summary (Docstring):\n{highest_bleu_instance['reference'][0]}\n")
        f.write(f"\nGenerated Summary (Comment):\n{highest_bleu_instance['generated']}\n")
        f.write("\n" + "="*50 + "\n\n")

    if highest_meteor_instance:
        f.write("\n=== HIGHEST METEOR SCORE INSTANCE ===\n")
        f.write(f"Score: {highest_meteor:.4f}\n")
        f.write(f"Original Code:\n{highest_meteor_instance['code']}\n")
        f.write(f"\nRefactored Code:\n{highest_meteor_instance['refactored_code']}\n")
        f.write(f"\nReference Summary (Docstring):\n{highest_meteor_instance['reference'][0]}\n")
        f.write(f"\nGenerated Summary (Comment):\n{highest_meteor_instance['generated']}\n")
        f.write("\n" + "="*50 + "\n")
