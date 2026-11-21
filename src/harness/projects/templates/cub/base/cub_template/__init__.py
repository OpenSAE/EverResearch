"""Purpose: Provision of software package portals for classification projects.

Scope of application: Scientific components to search for root directories while the source catalogue is running, and to use the inner component of the package once installed.
"""

from pathlib import Path as _Path

_checkout = _Path(__file__).resolve().parents[2]
if (_checkout / "conf/config.yaml").is_file():
    __path__.append(str(_checkout))
