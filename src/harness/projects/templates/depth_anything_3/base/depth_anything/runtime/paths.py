"""Resolve configuration in a source checkout or an installed distribution."""

from __future__ import annotations

from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


def _is_checkout(path: Path) -> bool:
    return (path / "base/depth_anything/interface.py").is_file() and (
        path / "conf/config.yaml"
    ).is_file()


SOURCE_ROOT = PACKAGE.parent.parent
CHECKOUT = SOURCE_ROOT if _is_checkout(SOURCE_ROOT) else None
CONFIG_ROOT = CHECKOUT / "conf" if CHECKOUT else PACKAGE / "conf"


def find_checkout() -> Path | None:
    """Locate the editable checkout or the checkout containing the current directory."""
    if CHECKOUT is not None:
        return CHECKOUT
    current = Path.cwd()
    return next((path for path in (current, *current.parents) if _is_checkout(path)), None)


def checkout_default(path: str) -> str:
    """Resolve a built-in workspace path from the checkout when available."""
    checkout = find_checkout()
    return str(checkout / path) if checkout is not None else path
