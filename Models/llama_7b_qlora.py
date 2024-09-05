
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig

# Define model ID
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

# Global variables for the model and tokenizer
b_model = None
b_tokenizer = None

def initialize_model():
    global b_model, b_tokenizer
    
    if b_model is None or b_tokenizer is None:
        # Quantization configuration
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4"
        )

        # Load model
        b_model = AutoModelForCausalLM.from_pretrained(model_id, quantization_config=quantization_config)

        # Load tokenizer
        b_tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        b_tokenizer.add_special_tokens({'pad_token': '<PAD>'})

        # Configure and add adapter
        lora_config = LoraConfig(
            r=8,
            target_modules=["q_proj", "o_proj", "k_proj", "v_proj", "gate_proj", "up_proj", "down_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        )
        b_model.add_adapter(lora_config)

def generate_text_with_llama(prompt: str, max_length: int = 50) -> str:
    # Ensure the model and tokenizer are initialized
    initialize_model()
    
    # Encode the input prompt
    inputs = b_tokenizer(prompt, return_tensors="pt")
    
    # Generate text
    with torch.no_grad():
        outputs = b_model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            top_k=50
        )
    
    # Decode the output
    generated_text = b_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return generated_text

