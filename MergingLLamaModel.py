from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM

base_model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
path = "TinyLlamaJokster"

#Load our Model
tokenizer = AutoTokenizer.from_pretrained(path)

#Create an object with both models
peft_model = PeftModel.from_pretrained(base_model, path)

#Merge models
merged_model = peft_model.merge_and_unload()
print("Models Merged")

merged_model.save_pretrained("BigLlamaJokster")
tokenizer.save_pretrained("BigLlamaJokster")
print("Models Saved")