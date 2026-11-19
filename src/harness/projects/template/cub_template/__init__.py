"""目的：提供分类项目的软件包入口。

适用范围：源码目录运行时查找根目录的科研组件，安装后使用包内组件。
"""

from pathlib import Path as _Path

_checkout = _Path(__file__).resolve().parents[1]
if (_checkout / "conf/config.yaml").is_file():
    __path__.append(str(_checkout))
