"""Purpose: Lightness of declaration of independence CNN Model.

Scope of application: Selection of current status through model registration CNN Series.
"""

from ...build import ModelSpec
from . import model

MODELS = (
    ModelSpec("small_cnn", model.CLASSES, model.build, model.validate_config, {"channels": 16}),
)
