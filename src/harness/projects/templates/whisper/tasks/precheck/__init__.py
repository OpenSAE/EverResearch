"""Check speech inputs and exercise the selected model on one bounded audio sample."""

from shutil import which

from ..audio import N_FRAMES, SAMPLE_RATE, load_audio, log_mel_spectrogram, pad_or_trim
from ..decoding import DecodingOptions


def require_audio_decoder():
    """Check that the program used by the shared audio loader is available."""
    if which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required to read Whisper audio inputs")


def read_sample(audio_path):
    """Decode no more than one second of the selected input."""
    sample = load_audio(audio_path, max_seconds=1)
    if not sample.size:
        raise ValueError(f"No audio samples could be decoded from {audio_path}")
    return sample


def check_sample(sample, model, *, task, language, fp16):
    """Check the feature and decoding contracts with one model output token."""
    features = log_mel_spectrogram(sample, n_mels=model.dims.n_mels)
    features = pad_or_trim(features, N_FRAMES).to(model.device)
    result = model.decode(
        features,
        DecodingOptions(
            task=task,
            language=language,
            fp16=fp16 and model.device.type != "cpu",
            sample_len=1,
            temperature=0,
        ),
    )
    return {
        "samples_checked": 1,
        "audio_seconds": float(sample.size / SAMPLE_RATE),
        "mel_bands": features.shape[0],
        "language": result.language,
        "output_tokens": len(result.tokens),
    }
