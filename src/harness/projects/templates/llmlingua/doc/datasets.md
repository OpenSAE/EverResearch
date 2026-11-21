# Data used by compression and training

The batch reader accepts a list of JSON objects with an integer-compatible `idx` and a selected input field. The field accepts a string, a list of strings, or null. Null rows are skipped. Indexes remain stable and all reference fields carry through to the compressed output.

- **Grade School Math (`gsm8k`)** supplies the demonstration prompt and separately identified test question in the saved README Quick Start. The model compresses the demonstrations. The test question remains reference information for downstream evaluation.
- **MeetingBank (`meetingbank`)** supplies transcripts as prompts, with summaries and segment identifiers retained as metadata. The saved transcript compression run uses three test records.
- **MeetingBank classifier training** aligns compressed text to original word labels and expands labels to subwords. Training and model selection use the historical shuffled chunk split. Claims that need meeting-level separation require a split retaining meeting identity.

The [experiment guide](experiment.md) locates the saved results and their recorded source versions.


The [prompt annotation package](../datasets/prompt_annotation/) formats MeetingBank transcripts and contains the alignment and filtering used by the two classifier workflows. The [training data adapter](../datasets/classifier_training/__init__.py) retains the shuffled 80/20 split for MeetingBank and 90/10 split for SecurityLingua.
