"""保存 ExtractStructure 导出的独立页面及其来源，记录对具体版本的审阅决定。

用于已登记项目的本地结构成果。调用方提供可信的独立 HTML、源码版本和分析范围。
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
        raise ProjectError(f"项目尚未登记：{project_id}")
    return f".workspace/harness/projects/structure/reviews_{project_id}"


def register(harness, project_id, html, revision, scope):
    base = folder(harness, project_id)
    source = Path(html).expanduser().resolve(strict=True)
    if source.suffix.lower() != ".html" or not revision.strip() or not scope.strip():
        raise ProjectError("请提供独立 HTML、源码版本或快照标识以及分析范围")
    content = source.read_bytes()
    if not content.strip():
        raise ProjectError("结构页面为空")
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
        raise ProjectError(f"结构页面与登记的版本不一致：{page}")
    decision = harness.resolve(f"{base}/decision.json")
    review = json.loads(decision.read_text()) if decision.exists() else None
    if review and review["sha256"] != record["sha256"]:
        raise ProjectError(f"审阅记录引用不同的结构页面版本：{page}")
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
