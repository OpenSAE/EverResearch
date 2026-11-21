"""Run LLMLingua-2 compression over indexed benchmark prompts."""


def compress_samples(compressor, samples, text_key, output_key, options):
    for index, sample in samples.items():
        compressed = compressor.compress_prompt_llmlingua2(sample[text_key], **options)
        result = dict(sample)
        result[output_key] = compressed["compressed_prompt"]
        segments = compressed["compressed_prompt_list"]
        if text_key == "prompt_list" and segments is not None:
            result["compressed_prompt_list"] = segments
        yield index, result
