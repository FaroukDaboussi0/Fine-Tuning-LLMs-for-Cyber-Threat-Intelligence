import pandas as pd
from Models.GeminiApi import bard
from Models.llama_7b_qlora import generate_text_with_llama
from Models.llama_7b_qlora_CTI import generate_text_with_llama_CTI




def evaluate_model(model, benchmark_path):
    # Load benchmark data
    benchmark_data = pd.read_csv(benchmark_path, delimiter='\t')
    
    # Initialize variables
    correct_answers = 0
    total_questions = len(benchmark_data)
    
    # Evaluate each question in the benchmark
    for _, row in benchmark_data.iterrows():
        prompt = row['Prompt']
        ground_truth_option = row['GT'].split()  
        
        # Generate text based on the model type
        if model == "Meta-Llama-3.1-8B-Instruct":
            generated_text = generate_text_with_llama(prompt)
        elif model == "llama-7b-qlora-CTI":
            generated_text = generate_text_with_llama_CTI(prompt)
        else:
            generated_text = bard(prompt)
        
        # Check if the generated text matches any ground truth options
        if generated_text.strip() == ground_truth_option:
            correct_answers += 1
    
    # Calculate and return the score
    score = correct_answers / total_questions if total_questions > 0 else 0
    return score


