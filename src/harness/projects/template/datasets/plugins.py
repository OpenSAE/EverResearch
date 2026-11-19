"""正式数据集标识，供项目登记入口读取。"""

from . import cub200
from .cub200 import offline_samples

DATASETS = {"cub200": cub200, "synthetic": offline_samples}
