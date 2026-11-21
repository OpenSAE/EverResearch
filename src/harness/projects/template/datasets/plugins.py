"""Official data set identifier for access to project registration portals."""

from . import cub200
from .cub200 import offline_samples

DATASETS = {"cub200": cub200, "synthetic": offline_samples}
