import torch
from datasets import load_dataset, Dataset
from peft import LoraConfig, PeftModel
from trl import SFTTrainer
from transformers import AutoTokenizer, TrainingArguments, AutoModelForCausalLM

datasets = "shuttie/dadjokes"
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
output_model = "TinyLlamaJokster"

# Preparing training data
def prepare_training_data(data_id):
    data = load_dataset(data_id, split="train")
    data_df = data.to_pandas()
    data_df["question"] = data_df["question"].fillna("")
    data_df["response"] = data_df["response"].fillna("")
    data_df["text"] = data_df[["question", "response"]].apply(
        lambda x: "<|im_start|>user\nHere is a joke. Try to guess the answer:\n" +
                  x["question"] + "<|im_end|>\n<|im_start|>assistant\n" + x["response"],
        axis=1
    )
    return Dataset.from_pandas(data_df)

data = prepare_training_data(datasets)

# Model and tokenizer loading
def get_model_and_tokenizer(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.float16,  # Use float16 to reduce memory usage
        device_map="auto"          # Automatically map to CUDA if available
    )
    model.config.use_cache = False
    model.config.pretraining_tp = 1
    return model, tokenizer

model, tokenizer = get_model_and_tokenizer(model_id)

# LoRA Configuration (keep light for Jetson Nano)
peft_config = LoraConfig(
    r=4,                        # Lower rank to save memory
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

# Training configuration
training_arguments = TrainingArguments(
    output_dir=output_model,
    per_device_train_batch_size=2,           # Small batch size for Jetson Nano
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,           # Accumulate to simulate larger batch
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    optim="adamw_torch",
    num_train_epochs=2,
    max_steps=75,
    logging_steps=10,
    save_strategy="no",
    fp16=True,                               # Enable AMP (Jetson Orin supports it)
    gradient_checkpointing=True,             # Reduce memory usage
    report_to="none"
)

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    args=training_arguments,
    train_dataset=data,
    peft_config=peft_config
)

# Run training
trainer.train()

# Save results
trainer.model.save_pretrained(output_model)
tokenizer.save_pretrained(output_model)
