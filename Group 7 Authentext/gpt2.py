import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def humanize_text(input_text):
    model_name = 'gpt2-large'
    tokenizer = GPT2Tokenizer.from_pretrained(model_name)
    model = GPT2LMHeadModel.from_pretrained(model_name)

    # Set pad token explicitly
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id

    # Constructing the paraphrasing prompt
    prompt = f"Paraphrase the following text while keeping its meaning and length similar:\n{input_text}\nParaphrased version:"

    inputs = tokenizer(prompt, return_tensors='pt', padding=True, truncation=True)

    word_count = len(input_text.split())

    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask, 
            max_new_tokens=int(word_count * 1.2),  # Dynamically controls output length
            num_beams=5,  # Improves paraphrasing quality
            no_repeat_ngram_size=2,
            temperature=0.85,
            top_p=0.95,
            top_k=70,
            repetition_penalty=1.2
        )

    humanized_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Remove unwanted prompt text if necessary
    if "Paraphrased version:" in humanized_text:
        humanized_text = humanized_text.split("Paraphrased version:")[1].strip()

    return humanized_text

if __name__ == "__main__":
    input_text = "Air pollution occurs when harmful substances like carbon monoxide, sulfur dioxide, and particulate matter contaminate the air. It is mainly caused by vehicle emissions, industrial activities, and the burning of fossil fuels. Prolonged exposure to polluted air can lead to serious health issues, including respiratory diseases and heart problems. Additionally, air pollution contributes to environmental problems such as acid rain, global warming, and ozone layer depletion. To reduce air pollution, it is essential to adopt renewable energy sources, promote public transportation, and enforce stricter environmental regulations."
    
    humanized_output = humanize_text(input_text)

    print("Original Text:", input_text)
    print("Humanized Text:", humanized_output)
