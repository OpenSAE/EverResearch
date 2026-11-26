# Whisper experiment records

## Purpose and main function

Choose and run a Whisper workload with a recorded configuration, automatic precheck, measured runtime, and readable outputs.

## Scope of application

Use a named run for one audio input or select a complete publisher test split for transcription, translation, subtitles, language identification, or recognition evaluation.

From the checkout, run:

```sh
whisper tests/fixtures/speech/jfk.flac --model tiny.en --device cpu --threads 2 \
  --output_format json --experiment speech_sample
whisper --inspect-run experiment/audio/whisper/speech/speech_sample
```

The command checks one second of audio with the chosen model before running full inference. Use `--precheck` with audio and model options to run just that stage. An experiment stores the effective options in `config.json`, the input and results status in `metadata/manifest.json`, precheck evidence in `reports/precheck.json`, and the transcript formats in `artifacts/`. For example, `artifacts/transcript_json.json` contains the text, segments and detected language. From another directory, pass the checkout as `--project-root PATH`. For another run, choose a new descriptive purpose.

The ordinary command also supports multiple inputs and `--output_dir PATH`; it writes each transcript under the original audio basename.

## Formal run choices

Reference timings were measured during adoption. Reproduce them with the data, weights, and commands below; run artifacts belong to your copied project.
Start from the publisher’s complete test split and use the checkpoint identified in the table. Each choice makes one pass. Transcription, translation, timestamps, and language identification process one recording at a time. The LibriSpeech evaluation uses batches of 16 and zero loader workers, like the English evaluation notebook. All six choices can run independently. The evaluation reads the publisher’s audio and references directly using its own short-form settings.

These estimates cover one NVIDIA GeForce RTX 5090 with 32 GB of memory, Python 3.12.15, PyTorch 2.10.0 with CUDA 12.8, half-precision inference, four PyTorch CPU threads, and local storage. They include process startup, audio inventory, checkpoint verification and loading, the bounded precheck, audio decoding, inference, and output writes. Download and extraction times are given separately below.

| Formal run | Complete workload and outputs | Bounded measurement | Estimated full wall time |
| --- | --- | --- | --- |
| English transcription | LibriSpeech `test-clean`, **2,620 recordings / 5.40 h**. `turbo` writes text and segment timestamps. | 10 recordings / 93.4 s of audio in **11.11 s**. Startup and precheck 8.82 s, measured processing 1.79 s. Timings · Wall clock | **5–10 min** |
| Korean transcription | FLEURS `ko_kr` test, **382 recordings / 1.33 h**. `medium` writes Korean text and segment timestamps. | 10 recordings / 126.2 s of audio in **12.55 s**. Startup and precheck 6.39 s, measured processing 5.74 s. Timings · Wall clock | **3–6 min** |
| Korean-to-English translation and BLEU | FLEURS `ko_kr` test, **382 recordings / 1.33 h**, matched to `en_us` test references. `medium` writes English text, segment timestamps, and a corpus BLEU score. | 10 recordings / 126.2 s of audio in **11.94 s**. Startup and precheck 7.38 s, measured processing 4.14 s. Timings · Wall clock | **2–4 min** |
| Word timestamps and subtitles | LibriSpeech `test-clean`, **2,620 recordings / 5.40 h**. `turbo` writes time-aligned word records and **5,240** SRT and WebVTT files in one ZIP. | 10 recordings / 93.4 s of audio in **11.11 s**. Startup and precheck 6.74 s, measured processing 3.90 s. Timings · Wall clock | **8–15 min** |
| English word error rate | LibriSpeech `test-clean`, **2,620 recordings / 5.40 h** in **164 batches**. `base.en` writes hypotheses, references, normalized text, and corpus word error counts. | 16 recordings / 98.7 s of audio in **3.22 s**. Startup and precheck 2.65 s, measured processing 0.18 s. Timings · Wall clock | **25–60 s** |
| Spoken language identification | FLEURS `ko_kr` test, **382 recordings / 1.33 h**. `turbo` scores language from the first 30-second window and writes a language probability distribution per recording and Korean recall. | 10 recordings / 126.2 s of audio in **7.64 s**. Startup and precheck 6.67 s, measured processing 0.56 s. Timings · Wall clock | **25–40 s** |

The projections add one startup and scale the measured processing to the complete split. For the two English transcription modes, the 30.04-second recording was the longest sample and the most expensive. The other nine took an average of 0.151 s for transcripts or 0.233 s for word timestamps and subtitle writes. Only nine of the 2,620 full-split recordings exceed 30 seconds, so the projections weight those separately and include subtitle ZIP creation. The Korean samples contain 126.2 s of audio and are close to the full split’s mean duration per recording. The error-rate projection scales one observed batch of 16 to the 164 full-split batches and includes scoring and writing the normalized text. The ranges allow for decoding fallback, recording length, batch variation, and local storage. The bounded measurements cover one full batch for the error-rate run and ten recordings for each other task.

The Korean choices use the locale selected in the project’s multilingual notebook. The translation writes English hypotheses, keeps the publisher’s Korean text, and scores corpus BLEU against official English test references joined by utterance ID. All 382 Korean test recordings have a match. The score covers Korean-to-English speech translation on this one split. The language identification result measures top-choice Korean recall and preserves the full predicted distribution for each recording. The English evaluation uses corpus word error rate (WER), calculated from substitutions, deletions, and insertions over the normalized reference word count. It applies the notebook’s `EnglishTextNormalizer` and pads or trims each recording to 30 seconds before decoding without timestamps. [English evaluation notebook](../../scripts/examples/librispeech_evaluation.ipynb) · [Multilingual example](../../scripts/examples/multilingual_speech.ipynb)

### Prepare the inputs

Activate the [project environment](../environment/README.md) and run these commands from the project root. Set the locations to existing copies if the two test splits or official checkpoints are already available. Named checkpoints are fetched and verified by Whisper when missing. The timing profiles used locally cached weights after data preparation.

```bash
python -m pip install jiwer==4.0.0 soundfile==0.14.0 sacrebleu==2.5.1

staging="${WHISPER_DATA_ROOT:-$PWD/../data/whisper}"
mkdir -p "$staging/librispeech" "$staging/fleurs/korean" "$staging/checkpoints"
curl -fL https://www.openslr.org/resources/12/test-clean.tar.gz \
  -o "$staging/librispeech/test-clean.tar.gz"
tar -xzf "$staging/librispeech/test-clean.tar.gz" -C "$staging/librispeech"
curl -fL https://storage.googleapis.com/xtreme_translations/FLEURS102/ko_kr.tar.gz \
  -o "$staging/fleurs/ko_kr.tar.gz"
tar -xzf "$staging/fleurs/ko_kr.tar.gz" -C "$staging/fleurs/korean" \
  --wildcards '*/test.tsv' '*/test/*.wav'
curl -fL https://huggingface.co/datasets/google/fleurs/resolve/70bb2e84b976b7e960aa89f1c648e09c59f894dd/data/en_us/test.tsv \
  -o "$staging/fleurs/english_test.tsv"
```

The LibriSpeech archive (347 MB) took about **125 s to download** and **2 s to extract**. The FLEURS locale archive (1.77 GB) took about **56 s to download** and **14 s to extract** its test audio and annotations. The split is based on the archive’s creation and last-write times and the observed combined duration. The English labels downloaded in under one second. The `medium` and `base.en` weights (1.67 GB combined) downloaded concurrently in **39.9 s**. The 1.62 GB Turbo checkpoint was already present. Weights are verified during startup. Download durations depend on the mirror and network. [OpenSLR LibriSpeech](https://openslr.org/12/) · [Google FLEURS](https://huggingface.co/datasets/google/fleurs) · [Official checkpoint catalog](../../models/whisper/weights.py)

### Start a selected run

Set the input and cache locations before choosing a command. The preparation above provides both dataset paths. Choose a writable model cache. The commands acquire and reuse the official Turbo, Medium and Base English weights as needed.

```bash
staging="${WHISPER_DATA_ROOT:-$PWD/../data/whisper}"
libri="$staging/librispeech/LibriSpeech/test-clean"
fleurs="$staging/fleurs/korean/ko_kr"
weights="$staging/checkpoints"
turbo_weights="${WHISPER_MODEL_DIR:-$PWD/../data/whisper/checkpoints}"
export OMP_NUM_THREADS=4

python scripts/run_speech_workload.py transcribe --corpus librispeech --data-root "$libri" \
  --model turbo --model-dir "$turbo_weights" --language en --purpose english_transcription
python scripts/run_speech_workload.py transcribe --corpus fleurs --data-root "$fleurs" \
  --model medium --model-dir "$weights" --language ko --purpose korean_transcription
python scripts/run_speech_workload.py translate --corpus fleurs --data-root "$fleurs" \
  --model medium --model-dir "$weights" --language ko --purpose korean_translation \
  --english-references "$staging/fleurs/english_test.tsv"
python scripts/run_speech_workload.py timestamps --corpus librispeech --data-root "$libri" \
  --model turbo --model-dir "$turbo_weights" --language en --purpose word_subtitles
python scripts/run_speech_workload.py evaluate --corpus librispeech --data-root "$libri" \
  --model base.en --model-dir "$weights" --language en --purpose recognition_error
python scripts/run_speech_workload.py identify --corpus fleurs --data-root "$fleurs" \
  --model turbo --model-dir "$turbo_weights" --language ko --purpose language_identification
```

Supply a new descriptive `--purpose` for repeated runs. `--samples 10` selects evenly spaced rows across the ordered publisher split and rounds up to a full batch. The English evaluation therefore uses 16 recordings in one batch. The bounded runs used `timeout --signal=INT --kill-after=3s 297s` around each Python command, allowing up to three seconds to save the interruption record within the five-minute limit. Recordings stay intact. `whisper --inspect-run experiment/audio/whisper/speech/<purpose>` reads the saved configuration and result manifest. The JSON Lines file includes each original input path and duration. The subtitle option additionally writes one ZIP containing SRT and WebVTT for each recording.
