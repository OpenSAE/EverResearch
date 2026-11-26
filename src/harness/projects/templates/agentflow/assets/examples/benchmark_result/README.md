# Bamboogle benchmark response example

## Purpose and main function

Keep one native AgentFlow benchmark result for checking the scoring reader against a
saved response.

## Scope of application

Use [output_0.json](files/output_0.json) to replay the read step for the first bundled
Bamboogle question. The template trial generated this response with the locally served
HuggingFaceTB/SmolLM2-135M-Instruct baseline. It preserves the response as produced, including the incorrect prediction.
See the [maintenance guide](../../../doc/maintenance.md#read-a-saved-benchmark-response)
for a command that reads the result without contacting a scoring service.
