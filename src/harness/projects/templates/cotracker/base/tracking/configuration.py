"""Resolve CoTracker configuration from the checkout or installed package."""

from importlib.resources import files


def configuration_path(source_path, *package_parts):
    if source_path.is_file():
        return source_path
    return files("cotracker").joinpath(*package_parts)
