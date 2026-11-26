"""Load local Qwen2.5-VL weights for MathVista image or text requests."""

from time import perf_counter
import logging


class QwenVisionModel:
    """Run one deterministic input at a time through the official checkpoint."""

    def __init__(self, weights, device, max_new_tokens, max_pixels):
        try:
            import torch
            from transformers import AutoConfig, AutoProcessor, Qwen2_5_VLForConditionalGeneration
        except ImportError as error:
            raise ValueError("Install the optional MathVista qwen runtime before loading local weights.") from error

        started = perf_counter()
        self.torch = torch
        self.device = torch.device(device)
        self.max_new_tokens = max_new_tokens
        if self.device.type == "cuda" and not torch.cuda.is_available():
            raise ValueError("The selected CUDA device is unavailable.")
        if max_new_tokens < 1:
            raise ValueError("--max_new_tokens must be positive.")

        config = AutoConfig.from_pretrained(weights, local_files_only=True)
        if config.model_type != "qwen2_5_vl":
            raise ValueError(f"Expected Qwen2.5-VL weights, found {config.model_type} at {weights}.")
        dtype = torch.bfloat16 if self.device.type == "cuda" else torch.float32
        self.processor = AutoProcessor.from_pretrained(weights, local_files_only=True)
        self.processor.image_processor.size["longest_edge"] = max_pixels
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            weights, local_files_only=True, use_safetensors=True, dtype=dtype,
            device_map={"": str(self.device)},
        ).eval()
        self.request_count = 0
        logging.info("Loaded Qwen2.5-VL on %s (%s) from %s in %.3f s",
                     self.device, dtype, weights, perf_counter() - started)

    def get_response(self, user_prompt, decoded_image=None):
        started = perf_counter()
        content = [{"type": "text", "text": user_prompt}]
        if decoded_image is not None:
            content.insert(0, {"type": "image"})
        messages = [{"role": "user", "content": content}]
        prompt = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
        )
        images = [decoded_image.convert("RGB")] if decoded_image is not None else None
        inputs = self.processor(text=[prompt], images=images, return_tensors="pt").to(self.device)
        with self.torch.inference_mode():
            output = self.model.generate(
                **inputs, max_new_tokens=self.max_new_tokens,
                do_sample=False, temperature=None, top_p=None, top_k=None,
            )
        completion = output[:, inputs["input_ids"].shape[-1]:]
        response = self.processor.batch_decode(completion, skip_special_tokens=True)[0].strip()
        self.request_count += 1
        logging.info("Qwen request %d: %d new tokens in %.3f s",
                     self.request_count, completion.shape[-1], perf_counter() - started)
        if self.device.type == "cuda" and self.request_count == 1:
            logging.info("Qwen peak CUDA allocation after the first request: %.2f GiB",
                         self.torch.cuda.max_memory_allocated(self.device) / 2**30)
        return response
