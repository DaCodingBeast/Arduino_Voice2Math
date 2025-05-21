import torch
from datasets import load_dataset, Dataset
from peft import LoraConfig, PeftModel
from trl import SFTTrainer
from transformers import AutoTokenizer,TrainingArguments, AutoModelForCausalLM

datasets = "shuttie/dadjokes"
model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
output_model = "TinyLlamaJokster"



# Taking data from HuggingFace
def prepare_training_data(data_id):
    data = load_dataset(data_id, split="train")
    data_df = data.to_pandas()
    data_df["question"] = data_df["question"].fillna("")
    data_df["response"] = data_df["response"].fillna("")
    data_df["text"] = data_df[["question", "response"]].apply(
        lambda x: "<|im_start|>user\n" + "Here is a joke. Try to guess the answer:\n" + x["question"] + "<|im_end|>\n<|im_start|>assistant\n" + x["response"],
        axis=1
    )
    data = Dataset.from_pandas(data_df)
    return data

data = prepare_training_data(datasets)
print("prepared training data")

# Access model
def get_model_and_tokenizer(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token
    base_model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
    base_model.config.use_cache = False
    base_model.config.pretraining_tp =1
    return base_model,tokenizer

model, tokenizer = get_model_and_tokenizer(model_id)

peft_config = LoraConfig(r=8,lora_alpha=16, lora_dropout=.05, bias = "none", task_type="CAUSAL_LM")
training_arguments = TrainingArguments(
    output_dir=output_model,
    per_device_eval_batch_size=16,                  # double batch size to reduce steps
    gradient_accumulation_steps=2,                 # reduce accumulation to process batches faster
    optim="adamw_torch",
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    save_strategy="no",                            # disable saving to save time
    logging_steps=10,                               # more frequent logs for short runs
    num_train_epochs=2,                            # keep it minimal
    max_steps=75,                                  # hard cap to stay within 30 mins
    fp16=True                                      # enable mixed precision if your GPU supports it
)
print("created trainer")
trainer = SFTTrainer(model = model, train_dataset=data, peft_config=peft_config, args = training_arguments)

trainer.train()
print("done training")

trainer.model.save_pretrained("TinyLlamaJokster")
tokenizer.save_pretrained("TinyLlamaJokster")