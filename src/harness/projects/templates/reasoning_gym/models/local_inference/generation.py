"""Load a local model and generate one response through vLLM.

The local evaluation task supplies the model path, sampling options, and chat.
"""


class LocalGeneration:
    def __init__(self, model_path, dtype, temperature, top_p, max_tokens):
        from vllm import LLM, SamplingParams

        self.model = LLM(model=model_path, dtype=dtype)
        self.tokenizer = self.model.get_tokenizer()
        self.sampling = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens)

    def generate(self, chat):
        prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        response = self.model.generate(prompt, self.sampling, use_tqdm=False)
        return response[0].outputs[0].text


class TransformersGeneration:
    """Run the same chat generation interface with a Transformers checkpoint."""

    def __init__(self, model_path, dtype, temperature, top_p, max_tokens, device):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=dtype).to(self.device).eval()
        self.options = {
            "max_new_tokens": max_tokens,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.eos_token_id,
        }
        if temperature > 0:
            self.options.update(temperature=temperature, top_p=top_p)

    def generate(self, chat):
        prompt = self.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt", add_special_tokens=False).to(self.device)
        with self.torch.inference_mode():
            response = self.model.generate(**inputs, **self.options)
        return self.tokenizer.decode(response[0, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
