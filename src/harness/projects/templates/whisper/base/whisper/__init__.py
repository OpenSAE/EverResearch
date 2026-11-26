"""Expose the Whisper speech-recognition API from its component implementations."""

from .audio import load_audio, log_mel_spectrogram, pad_or_trim
from .decoding import DecodingOptions, DecodingResult, decode, detect_language
from .model import ModelDimensions, Whisper
from .model.weights import _ALIGNMENT_HEADS as _ALIGNMENT_HEADS
from .model.weights import _MODELS as _MODELS
from .model.weights import _download as _download
from .model.weights import available_models as available_models
from .model.weights import load_model as load_model
from .transcribe import transcribe
from .version import __version__
