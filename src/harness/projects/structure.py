"""Save ExtractStructure Export of separate pages and their source to record review decisions for specific versions.

Use local structural results for registered projects. Callers provide credible independence HTML,Source version and analysis range.
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from ..central import ProjectError, identity
from ..core.workspace import save, save_bytes


def folder(harness, project_id):
    project_id = identity(project_id)
    if project_id not in harness.bindings():
        raise ProjectError(f"Projects not yet registered:{project_id}")
    return (harness.project_record(project_id) / "structure").relative_to(harness.root).as_posix()


def register(harness, project_id, html, revision, scope):
    base = folder(harness, project_id)
    source = Path(html).expanduser().resolve(strict=True)
    if source.suffix.lower() != ".html" or not revision.strip() or not scope.strip():
        raise ProjectError("Please be independent. HTML,Source version or snapshot identifier and analytical scope")
    content = source.read_bytes()
    if not content.strip():
        raise ProjectError("Structure page is empty")
    key = uuid4().hex
    page = harness.resolve(f"{base}/{key}/index.html")
    save_bytes(page, content, source=str(source))
    record = {
        "id": key,
        "project": project_id,
        "revision": revision.strip(),
        "scope": scope.strip(),
        "source": str(source),
        "sha256": hashlib.sha256(content).hexdigest(),
        "registered_at": datetime.now(timezone.utc).isoformat(),
    }
    save(harness.resolve(f"{base}/{key}/artifact.json"), record, source=__file__)
    return show(harness, project_id, key)


def show(harness, project_id, key, *, verify=True):
    base = f"{folder(harness, project_id)}/{identity(key)}"
    path = harness.resolve(f"{base}/artifact.json", exists=True)
    record = json.loads(path.read_text())
    page = harness.resolve(f"{base}/index.html", exists=True)
    if verify and hashlib.sha256(page.read_bytes()).hexdigest() != record["sha256"]:
        raise ProjectError(f"Structure page inconsistent with registered version:{page}")
    decision = harness.resolve(f"{base}/decision.json")
    review = json.loads(decision.read_text()) if decision.exists() else None
    if review and review["sha256"] != record["sha256"]:
        raise ProjectError(f"Review the records to refer to different structured pages:{page}")
    return {**record, "page": str(page), "review": review}


def list_reviews(harness, project_id):
    directory = harness.resolve(folder(harness, project_id))
    return sorted(
        (show(harness, project_id, item.parent.name, verify=False)
         for item in directory.glob("*/artifact.json")),
        key=lambda item: item["registered_at"], reverse=True,
    )


def review(harness, project_id, key, decision, note):
    record = show(harness, project_id, key)
    path = harness.resolve(f"{folder(harness, project_id)}/{key}/decision.json")
    save(path, {"decision": decision, "note": note,
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "sha256": record["sha256"]}, source=__file__)
    return show(harness, project_id, key)
