from transformers import AutoTokenizer, GenerationConfig, AutoModelForCausalLM
import re

class LLM_Jokster:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("BigLlamaJokster")
        self.model = AutoModelForCausalLM.from_pretrained("BigLlamaJokster")
        self.generation_config = GenerationConfig( 
            do_sample = True, 
            top_k = 15, 
            top_p = .8,
            temperature = .8, 
            repetition_penalty = 1.0, 
            max_new_tokens= 10, 
            pad_token_id = self.tokenizer.eos_token_id)

        
    def formatPrompt(question) ->str:
        return f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"

    def formatResponse(response) -> str:
        # Question mark identifies needed content
        match = re.search(r"<\|im_start\|>assistant\n(.*?)(<\|im_end\|>|$)", response, re.DOTALL)
        return match.group(1).strip() if match else response.strip()

    def askLLM(self, input) ->str : 
        promptEngineering = "Here is a joke (try to guess the answer to the joke)" +input 
        final_prompt = LLM_Jokster.formatPrompt(promptEngineering)
        
        model_inputs = self.tokenizer(final_prompt, return_tensors = "pt")

        outputs = self.model.generate(**model_inputs, generation_config = self.generation_config)

        decodedOutput = self.tokenizer.decode(outputs[0], skip_special_tokens = True)
        return LLM_Jokster.formatResponse(decodedOutput)
    

print(LLM_Jokster().askLLM("What do you call cheese that isn't yours?"))