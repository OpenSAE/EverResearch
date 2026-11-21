# ------------------------------------------------------------------------
# RF-DETR
# Copyright (c) 2025 Roboflow. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 [see LICENSE for details]
# ------------------------------------------------------------------------
"""Connect documentation pages, assets and cookbooks to their published routes."""

import json
from pathlib import Path
from shutil import copyfile
from typing import Any
from urllib.parse import quote, urljoin

from mkdocs.plugins import event_priority
from mkdocs.structure.files import File, Files

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_MAP = PROJECT_ROOT / "scripts/documentation/site_sources.json"


@event_priority(100)
def on_files(files: Files, config: Any) -> Files:
    """Register supplemental sources before the Markdown and notebook plugins inspect them."""
    docs = Path(config.docs_dir)
    routes = json.loads(SOURCE_MAP.read_text(encoding="utf-8"))
    for source, route in routes.items():
        source_path = PROJECT_ROOT / source
        if source_path.is_relative_to(docs):
            original = files.get_file_from_path(source_path.relative_to(docs).as_posix())
            if original is not None:
                files.remove(original)
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        file = File(route, config.docs_dir, config.site_dir, config.use_directory_urls)
        file.abs_src_path = str(source_path)
        files.append(file)
    return files


def on_page_context(context: dict[str, Any], page: Any, config: Any, nav: Any) -> dict[str, Any]:
    """Link the page edit control to the real Markdown or notebook source."""
    if config.repo_url and page.file.abs_src_path:
        source = Path(page.file.abs_src_path)
        if source.is_relative_to(PROJECT_ROOT):
            relative = quote(source.relative_to(PROJECT_ROOT).as_posix())
            page.edit_url = urljoin(f"{config.repo_url.rstrip('/')}/", f"edit/develop/{relative}")
    return context


@event_priority(-100)
def on_post_page(output: str, page: Any, config: Any) -> str:
    """Keep earlier notebook download URLs available after renaming source files."""
    route = Path(page.file.src_uri)
    if route.suffix != ".ipynb":
        return output
    destination = Path(page.file.abs_dest_path).parent
    download = destination / Path(page.file.abs_src_path).name
    legacy_download = destination / route.name
    if download != legacy_download and download.is_file():
        copyfile(download, legacy_download)
    return output
