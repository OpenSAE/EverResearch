"""Expose the MobileCLIP encoder at its former import location."""
import sys

from .. import mobile_clip
from ..mobile_clip import image_encoder

mobileclip = mobile_clip
sys.modules[f"{__name__}.mobileclip"] = mobile_clip
sys.modules[f"{__name__}.mobileclip.mci"] = image_encoder
