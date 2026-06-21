"""
Cockpit Run Desk — unified local web UI for multiple analytics projects.

Run from Cockpit root:
  python webui/server.py

Environment:
  ANALYSIS_WEB_PORT          listen port (default 8765)
  ANALYSIS_WEB_TOKEN         if set, POST /api/run requires Bearer token
  ANALYSIS_RUN_TIMEOUT_SEC   subprocess timeout (default 7200)
  ANALYSIS_WEB_OPEN_BROWSER  set to 1 to open browser on start

Listens on 127.0.0.1 only. Zero third-party dependencies.
"""

from __future__ import annotations

import html
import json
import mimetypes
import os
import re
import socket
import subprocess
import sys
import threading
import webbrowser
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = Path(__file__).resolve().parent
INDEX_HTML = WEB_DIR / "index.html"
WEB_ASSETS_ROOT = (WEB_DIR / "assets").resolve()
CONFIG_PATH = ROOT / "config" / "projects.json"

RUN_DESK_PROJECT_ID = "cockpit"
REGISTRY_VERSION = 1

_VIEWABLE_KINDS = {".pdf": "pdf", ".html": "html", ".csv": "csv", ".json": "json", ".md": "md"}
_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_FORMAT_ORDER = {"html": 0, "pdf": 1, "csv": 2, "json": 3}

# Loaded at import: project configs + merged analyses
PROJECTS: list[dict] = []
ANALYSES: list[dict] = []
_ANALYSES_BY_KEY: dict[str, dict] = {}
_ARTIFACT_ROOTS: dict[str, list[Path]] = {}


def _load_config() -> None:
    global PROJECTS, ANALYSES, _ANALYSES_BY_KEY, _ARTIFACT_ROOTS
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(f"Missing config: {CONFIG_PATH}")
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    PROJECTS.clear()
    ANALYSES.clear()
    _ANALYSES_BY_KEY.clear()
    _ARTIFACT_ROOTS.clear()

    for proj in cfg.get("projects", []):
        proj_root = Path(proj["root"]).resolve()
        reg_rel = proj.get("registry", "")
        reg_path = (ROOT / reg_rel).resolve() if not Path(reg_rel).is_absolute() else Path(reg_rel)
        reg_data = json.loads(reg_path.read_text(encoding="utf-8"))
        report_roots: list[Path] = []
        for rr in proj.get("report_roots", []):
            report_roots.append((proj_root / rr["path"]).resolve())
        _ARTIFACT_ROOTS[proj["id"]] = report_roots

        for entry in reg_data.get("analyses", []):
            merged = dict(entry)
            merged["project_id"] = proj["id"]
            merged["project_label"] = proj.get("label", proj["id"])
            merged["project_root"] = str(proj_root)
            merged["_key"] = f"{proj['id']}:{entry['id']}"
            ANALYSES.append(merged)
            _ANALYSES_BY_KEY[merged["_key"]] = merged

        PROJECTS.append({
            "id": proj["id"],
            "label": proj.get("label", proj["id"]),
            "short_label": proj.get("short_label", proj.get("label", proj["id"])),
            "dashboard_categories": proj.get("dashboard_categories", []),
            "output_probe": proj.get("output_probe"),
        })


_load_config()


def _check_token(headers) -> bool:
    token = os.environ.get("ANALYSIS_WEB_TOKEN")
    if not token:
        return True
    return headers.get("Authorization", "") == f"Bearer {token}"


def _report_group(analysis: dict, project_root: Path) -> str | None:
    """The report folder/file group this analysis writes into, if any."""
    explicit = analysis.get("report_group")
    if explicit:
        return explicit
    artifact = analysis.get("artifact")
    if not artifact:
        return None
    rel = artifact["path"].replace("\\", "/")
    parts = rel.split("/")
    for i, p in enumerate(parts):
        if p in ("reports", "analysis") and i + 1 < len(parts):
            if p == "analysis" and i + 2 < len(parts) and parts[i + 1] == "reports":
                return parts[i + 2] if i + 2 < len(parts) else None
            return parts[i + 1]
    if len(parts) > 1:
        return parts[0]
    return None


def _public_analysis_entry(analysis: dict) -> dict:
    params = [p for p in analysis.get("params", []) if p.get("type") != "info"]
    secondary = _resolve_secondary_artifacts(analysis, {})
    return {
        "id": analysis["id"],
        "project_id": analysis["project_id"],
        "project_label": analysis["project_label"],
        "label": analysis["label"],
        "category": analysis["category"],
        "description": analysis.get("description", ""),
        "params": params,
        "artifact_kind": (analysis.get("artifact") or {}).get("kind"),
        "report_group": _report_group(analysis, Path(analysis["project_root"])),
        "secondary_artifact_labels": [
            s.get("label") for s in (analysis.get("secondary_artifacts") or []) if s.get("label")
        ],
        "secondary_artifacts": secondary,
    }


def _public_registry() -> dict:
    return {
        "registry_version": REGISTRY_VERSION,
        "project_id": RUN_DESK_PROJECT_ID,
        "project_label": "Cockpit Run Desk",
        "projects": PROJECTS,
        "analyses": [_public_analysis_entry(a) for a in ANALYSES],
    }


def _artifact_url(project_id: str, rel: str) -> str:
    from urllib.parse import quote
    return f"/artifact?project={quote(project_id)}&path={quote(rel.replace(chr(92), '/'))}"


def _artifact_view_url(project_id: str, rel: str) -> str:
    from urllib.parse import quote
    return f"/artifact/view?project={quote(project_id)}&path={quote(rel.replace(chr(92), '/'))}"


def _companion_html_path(path: Path) -> Path | None:
    if path.suffix.lower() == ".json" and path.name.endswith("_results.json"):
        candidate = path.with_suffix(".html")
        if candidate.is_file():
            return candidate
    return None


def _inline_markdown(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def _render_markdown_html(text: str, title: str = "Report") -> bytes:
    lines = text.splitlines()
    parts = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        "<style>body{font-family:Segoe UI,system-ui,sans-serif;background:#0f1115;color:#eef2ff;"
        "padding:1.25rem 1.5rem;line-height:1.55;max-width:1100px;margin:0 auto}",
        "h1,h2,h3{color:#f8fafc;margin:1.4rem 0 0.6rem}h1{font-size:1.45rem}h2{font-size:1.15rem}"
        "h3{font-size:1rem}p,li{color:#d8deea}ul{padding-left:1.25rem}code{background:#1e2430;"
        "padding:0.1rem 0.35rem;border-radius:4px;font-size:0.9em}",
        "table{border-collapse:collapse;width:100%;font-size:0.82rem;margin:0.75rem 0 1.25rem}",
        "th,td{border:1px solid #2a3140;padding:0.4rem 0.55rem;text-align:left;vertical-align:top}",
        "th{background:#1e2430;color:#9aa4b8}</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
    ]
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        stripped = line.strip()
        if not stripped:
            idx += 1
            continue
        if stripped.startswith("|") and "|" in stripped[1:]:
            table_lines: list[str] = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                table_lines.append(lines[idx].strip())
                idx += 1
            if len(table_lines) >= 2:
                rows = [
                    [cell.strip() for cell in row.strip("|").split("|")]
                    for row in table_lines
                    if not re.match(r"^\|?[\s\-:|]+\|?$", row)
                ]
                if rows:
                    parts.append("<table><thead><tr>")
                    parts.extend(f"<th>{_inline_markdown(cell)}</th>" for cell in rows[0])
                    parts.append("</tr></thead><tbody>")
                    for row in rows[1:]:
                        parts.append("<tr>")
                        parts.extend(f"<td>{_inline_markdown(cell)}</td>" for cell in row)
                        parts.append("</tr>")
                    parts.append("</tbody></table>")
            continue
        if stripped.startswith("### "):
            parts.append(f"<h3>{_inline_markdown(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            parts.append(f"<h2>{_inline_markdown(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            parts.append(f"<h1>{_inline_markdown(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            parts.append(f"<ul><li>{_inline_markdown(stripped[2:])}</li></ul>")
        else:
            parts.append(f"<p>{_inline_markdown(stripped)}</p>")
        idx += 1
    parts.append("</body></html>")
    return "".join(parts).encode("utf-8")


def _render_artifact_html(project_id: str, candidate: Path) -> bytes | None:
    suffix = candidate.suffix.lower()
    if suffix == ".md":
        try:
            return _render_markdown_html(
                candidate.read_text(encoding="utf-8"),
                title=candidate.stem.replace("_", " "),
            )
        except OSError:
            return None
    project_root = None
    for analysis in ANALYSES:
        if analysis["project_id"] == project_id:
            project_root = Path(analysis["project_root"])
            break
    render_script = None
    if project_root:
        render_script = project_root / "scripts" / "reports" / "render_dq_report.py"
    if render_script and render_script.is_file():
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root / "scripts" / "reports"))
        try:
            from render_dq_report import render_csv_report, render_json_file_report

            if suffix == ".json":
                return render_json_file_report(candidate).encode("utf-8")
            if suffix == ".csv":
                title = candidate.stem.replace("_", " ")
                return render_csv_report(candidate, title).encode("utf-8")
        except Exception:
            pass
    if suffix == ".json":
        try:
            pretty = json.dumps(json.loads(candidate.read_text(encoding="utf-8")), indent=2)
            body = (
                "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                "<style>body{font-family:ui-monospace,Consolas,monospace;background:#0f1115;color:#eef2ff;padding:1rem}"
                "pre{white-space:pre-wrap;word-break:break-word}</style></head>"
                f"<body><pre>{pretty}</pre></body></html>"
            )
            return body.encode("utf-8")
        except (OSError, ValueError):
            return None
    if suffix == ".csv":
        import csv

        try:
            with candidate.open(newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))
            if not rows:
                return b"<html><body><p>Empty CSV</p></body></html>"
            headers, data = rows[0], rows[1:]
            parts = [
                "<!DOCTYPE html><html><head><meta charset='utf-8'>",
                "<style>body{font-family:Segoe UI,system-ui,sans-serif;background:#0f1115;color:#eef2ff;padding:1rem}",
                "table{border-collapse:collapse;width:100%;font-size:0.85rem}",
                "th,td{border:1px solid #2a3140;padding:0.4rem 0.55rem;text-align:left}",
                "th{background:#1e2430;color:#9aa4b8}</style></head><body>",
                f"<h1>{candidate.name}</h1><table><thead><tr>",
            ]
            parts.extend(f"<th>{h}</th>" for h in headers)
            parts.append("</tr></thead><tbody>")
            for row in data[:500]:
                parts.append("<tr>")
                parts.extend(f"<td>{cell}</td>" for cell in row)
                parts.append("</tr>")
            parts.append("</tbody></table></body></html>")
            return "".join(parts).encode("utf-8")
        except OSError:
            return None
    return None


def _list_reports(project_filter: str | None = None) -> dict:
    grouped: dict[tuple, dict] = {}

    for proj in PROJECTS:
        pid = proj["id"]
        if project_filter and project_filter not in ("all", pid):
            continue
        roots = _ARTIFACT_ROOTS.get(pid, [])
        for artifact_root in roots:
            if not artifact_root.is_dir():
                continue
            for path in artifact_root.rglob("*"):
                if not path.is_file():
                    continue
                kind = _VIEWABLE_KINDS.get(path.suffix.lower())
                if not kind:
                    continue
                name = path.name
                if name.lower().endswith("_for_pdf.html"):
                    continue
                if name.endswith("_results.json") and path.with_suffix(".html").is_file():
                    continue
                rel = path.relative_to(artifact_root).as_posix()
                parts = rel.split("/")
                group = parts[0] if len(parts) > 1 else "(root)"
                m = _DATE_RE.search(name)
                date_str = m.group(1) if m else ""
                label = path.stem
                if date_str:
                    label = label.replace(date_str, "").strip("_-. ")
                label = label or path.stem
                key = (pid, group, date_str, label)
                entry = grouped.get(key)
                if entry is None:
                    entry = {
                        "project_id": pid,
                        "project_label": proj["label"],
                        "group": group,
                        "date": date_str,
                        "label": label,
                        "title": label.replace("_", " ").strip() or group,
                        "formats": [],
                        "mtime": 0,
                    }
                    grouped[key] = entry
                entry["formats"].append({"kind": kind, "url": _artifact_url(pid, rel)})
                if kind in ("json", "csv"):
                    entry["formats"].append(
                        {"kind": "html", "url": _artifact_view_url(pid, rel), "label": "report"}
                    )
                try:
                    entry["mtime"] = max(entry["mtime"], int(path.stat().st_mtime))
                except OSError:
                    pass

    out = []
    for entry in grouped.values():
        entry["formats"].sort(key=lambda f: _FORMAT_ORDER.get(f["kind"], 9))
        entry["primary"] = entry["formats"][0]
        out.append(entry)
    out.sort(key=lambda e: (e["date"] or "", e["mtime"]), reverse=True)
    return {"reports": out}


def _svelte_output_roots(project_root: Path) -> dict[str, Path]:
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from lib.paths import ROUTINE_GEO_REVIEWS_DIR, ROUTINE_MONTHLY_PACKS_DIR, ROUTINE_ROLLUPS

    return {
        "routine_rollups": ROUTINE_ROLLUPS,
        "geo_reviews": ROUTINE_GEO_REVIEWS_DIR,
        "monthly_pack": ROUTINE_MONTHLY_PACKS_DIR,
    }


def _date_from_filename(name: str) -> str:
    m = _DATE_RE.search(name)
    return m.group(1) if m else ""


def _probe_output(spec: dict, project_root: Path) -> dict:
    try:
        roots = _svelte_output_roots(project_root)
    except Exception:
        return {"has_output": False, "last_date": None, "output_path": None}

    root_key = spec.get("root", "")
    root = roots.get(root_key)
    if root is None:
        return {"has_output": False, "last_date": None, "output_path": None}

    search_root = root
    if spec.get("month"):
        search_root = root / spec["month"]

    candidates: list[Path] = []
    if spec.get("glob"):
        if search_root.is_dir():
            candidates = sorted(search_root.glob(spec["glob"]), reverse=True)
    elif spec.get("file"):
        fname = spec["file"]
        if search_root.is_dir():
            candidates = sorted(search_root.glob(f"????-??-??_{fname}"), reverse=True)
            legacy = search_root / fname
            if legacy.is_file():
                candidates.append(legacy)

    if not candidates:
        return {"has_output": False, "last_date": None, "output_path": None}

    best = candidates[0]
    last_date = _date_from_filename(best.name)
    return {
        "has_output": True,
        "last_date": last_date or None,
        "output_path": str(best),
    }


def _dashboard_payload(project_filter: str | None = None) -> dict:
    today_str = date.today().isoformat()
    reports = _list_reports(project_filter)["reports"]
    reports_by_group: dict[tuple, list] = {}
    for r in reports:
        reports_by_group.setdefault((r["project_id"], r["group"]), []).append(r)

    sections: list[dict] = []
    for proj in PROJECTS:
        pid = proj["id"]
        if project_filter and project_filter not in ("all", pid):
            continue
        categories = proj.get("dashboard_categories") or []
        project_root = Path(next(a["project_root"] for a in ANALYSES if a["project_id"] == pid))

        for category in categories:
            jobs: list[dict] = []
            for analysis in ANALYSES:
                if analysis["project_id"] != pid or analysis["category"] != category:
                    continue
                job: dict = {
                    "id": analysis["id"],
                    "project_id": pid,
                    "label": analysis["label"],
                    "description": analysis.get("description", ""),
                    "artifact_kind": (analysis.get("artifact") or {}).get("kind"),
                    "report_group": _report_group(analysis, project_root),
                    "has_output": False,
                    "ran_today": False,
                    "last_date": None,
                    "latest_report": None,
                    "output_path": None,
                    "output_note": None,
                }
                rg = job["report_group"]
                if rg:
                    group = reports_by_group.get((pid, rg), [])
                    todays = next((r for r in group if r["date"] == today_str), None)
                    latest = group[0] if group else None
                    viewable = todays or latest
                    job["has_output"] = bool(viewable)
                    job["ran_today"] = bool(todays)
                    job["last_date"] = (todays or latest or {}).get("date")
                    job["latest_report"] = viewable
                elif analysis.get("output") and proj.get("output_probe") == "svelte":
                    probe = _probe_output(analysis["output"], project_root)
                    job["has_output"] = probe["has_output"]
                    job["last_date"] = probe["last_date"]
                    job["ran_today"] = probe["last_date"] == today_str if probe["last_date"] else False
                    job["output_path"] = probe["output_path"]
                else:
                    job["output_note"] = (
                        "Writes to Accounts/ — path appears in logs after run."
                        if proj.get("output_probe") == "svelte"
                        else "Check reports/ after run."
                    )
                jobs.append(job)
            if jobs:
                sections.append({
                    "category": category,
                    "project_id": pid,
                    "project_label": proj["label"],
                    "jobs": jobs,
                })

    return {"sections": sections, "reports": reports, "today": today_str}


def _qa_date_slug(brand: str, date_str: str, end_exclusive: str | None) -> str:
    if brand in ("goslim", "bbb", "getbodypath", "oad") and end_exclusive:
        last_inc = (date.fromisoformat(end_exclusive) - timedelta(days=1)).isoformat()
        return f"{date_str}_to_{last_inc}"
    return date_str


def _build_argv(analysis: dict, params: dict) -> tuple[list[str] | None, str | None]:
    project_root = Path(analysis["project_root"])
    script = project_root / analysis["script"]
    if not script.is_file():
        return None, f"script not found: {analysis['script']}"

    argv = [sys.executable, str(script)]
    for extra in analysis.get("extra_argv") or []:
        argv.append(str(extra))
    for spec in analysis.get("params", []) or []:
        name = spec["name"]
        ptype = spec["type"]
        if ptype == "info":
            continue
        flag = spec["flag"]
        if flag == "__skip_narrative_pdf__":
            continue
        raw = params.get(name)

        if ptype == "checkbox":
            if raw in (True, "true", "1", "on", "yes"):
                if flag.startswith("__"):
                    continue
                argv.append(flag)
            continue

        value = "" if raw is None else str(raw).strip()
        if value == "":
            if not spec.get("optional", True):
                return None, f"{spec.get('label', name)} is required"
            continue

        if ptype == "int":
            try:
                int(value)
            except ValueError:
                return None, f"{spec.get('label', name)} must be a whole number"
        if ptype == "date":
            try:
                date.fromisoformat(value)
            except ValueError:
                return None, f"{spec.get('label', name)} must be YYYY-MM-DD"
        argv.extend([flag, value])

    return argv, None


def _artifact_format_values(analysis: dict, params: dict) -> dict[str, str]:
    report_date = (params.get("report-date") or params.get("date") or "").strip()
    if not report_date:
        report_date = date.today().isoformat()
    brand = (params.get("brand") or "").strip().lower()
    end_exclusive = (params.get("end_exclusive") or "").strip() or None
    date_slug = _qa_date_slug(brand, report_date, end_exclusive) if brand else report_date
    monitor_date = report_date
    if not params.get("date") and analysis["id"] == "daily_conversion_monitor":
        monitor_date = (date.today() - timedelta(days=1)).isoformat()
    return {
        "report-date": report_date,
        "date": monitor_date,
        "brand": brand,
        "date_slug": date_slug,
    }


def _artifact_candidate_path(
    artifact: dict,
    project_root: Path,
    fmt: dict[str, str],
) -> Path | None:
    candidate: Path | None = None
    if artifact.get("glob"):
        pattern = artifact["glob"]
        for key, val in fmt.items():
            pattern = pattern.replace("{" + key + "}", val)
        matches = [p for p in project_root.glob(pattern) if p.is_file()]
        if matches:
            candidate = max(matches, key=lambda p: p.stat().st_mtime)
    elif artifact.get("path"):
        rel = artifact["path"]
        for key, val in fmt.items():
            rel = rel.replace("{" + key + "}", val)
        candidate = (project_root / rel).resolve()
    return candidate


def _artifact_url_for_candidate(
    candidate: Path,
    artifact: dict,
    project_id: str,
    allowed: list[Path],
) -> tuple[str | None, str | None]:
    for root in allowed:
        try:
            rel_to_root = candidate.relative_to(root).as_posix()
        except ValueError:
            continue
        html_companion = _companion_html_path(candidate)
        if html_companion:
            try:
                html_rel = html_companion.relative_to(root).as_posix()
                return _artifact_url(project_id, html_rel), "html"
            except ValueError:
                pass
        kind = artifact.get("kind")
        if kind in ("json", "csv", "md", "markdown"):
            return _artifact_view_url(project_id, rel_to_root), "html"
        return _artifact_url(project_id, rel_to_root), kind
    return None, None


def _resolve_artifact_spec(
    artifact: dict,
    project_id: str,
    project_root: Path,
    fmt: dict[str, str],
) -> tuple[str | None, str | None]:
    candidate = _artifact_candidate_path(artifact, project_root, fmt)
    if candidate is None or not candidate.is_file():
        return None, None
    allowed = _ARTIFACT_ROOTS.get(project_id, [])
    return _artifact_url_for_candidate(candidate, artifact, project_id, allowed)


def _resolve_artifact(analysis: dict, params: dict) -> tuple[str | None, str | None]:
    artifact = analysis.get("artifact")
    if not artifact:
        return None, None

    project_root = Path(analysis["project_root"])
    fmt = _artifact_format_values(analysis, params)
    return _resolve_artifact_spec(artifact, analysis["project_id"], project_root, fmt)


def _resolve_secondary_artifacts(analysis: dict, params: dict) -> list[dict]:
    specs = analysis.get("secondary_artifacts") or []
    if not specs:
        return []
    project_root = Path(analysis["project_root"])
    project_id = analysis["project_id"]
    fmt = _artifact_format_values(analysis, params)
    out: list[dict] = []
    for spec in specs:
        url, kind = _resolve_artifact_spec(spec, project_id, project_root, fmt)
        if url:
            out.append({
                "label": spec.get("label") or "Output",
                "url": url,
                "kind": kind or spec.get("kind"),
            })
    return out


def _run_funnel_narrative_pdf(analysis: dict, params: dict) -> tuple[str | None, str | None, str, str]:
    project_root = Path(analysis["project_root"])
    project_id = analysis["project_id"]
    brand = (params.get("brand") or "").strip().lower()
    date_str = (params.get("date") or "").strip()
    end_exclusive = (params.get("end_exclusive") or "").strip() or None
    if params.get("skip-pdf") in (True, "true", "1", "on", "yes"):
        return None, None, "", "Skipped narrative PDF"

    date_slug = _qa_date_slug(brand, date_str, end_exclusive)
    json_name = f"qa_export_{brand}_{date_slug}.json"
    json_path = project_root / "reports" / json_name
    if not json_path.is_file():
        return None, None, "", f"Export JSON not found: {json_name}"

    script_map = {
        "goslim": "generate_qa_report_goslim_narrative_pdf.py",
        "bbb": "generate_qa_report_bbb_narrative_pdf.py",
        "getbodypath": "generate_qa_report_getbodypath_narrative_pdf.py",
        "oad": "generate_qa_report_oad_narrative_pdf.py",
    }
    script_name = script_map.get(brand)
    if not script_name:
        return None, None, "", f"No narrative PDF script for brand {brand}"

    pdf_script = project_root / "python" / script_name
    timeout = int(os.environ.get("QA_PDF_TIMEOUT_SEC", "600"))
    proc = subprocess.run(
        [sys.executable, str(pdf_script), "--json", str(json_path)],
        cwd=str(project_root),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=os.environ.copy(),
    )
    expected = project_root / "reports" / f"qa-report-{brand}-{date_slug}.pdf"
    if expected.is_file() and proc.returncode == 0:
        rel = expected.relative_to(project_root / "reports").as_posix()
        return _artifact_url(project_id, rel), "pdf", proc.stdout or "", proc.stderr or ""
    err = (proc.stderr or "") + (f"\n(exit {proc.returncode})" if proc.returncode else "")
    return None, None, proc.stdout or "", err


def _resolve_artifact_path(project_id: str, rel: str) -> Path | None:
    rel = rel.strip().lstrip("/").replace("\\", "/")
    if not rel or ".." in rel.split("/"):
        return None
    for root in _ARTIFACT_ROOTS.get(project_id, []):
        candidate = (root / rel).resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


def _port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) != 0


def _launch_server_py(current_port: int) -> dict:
    script = ROOT / "start_run_desk.ps1"
    if not script.is_file():
        raise FileNotFoundError("start_run_desk.ps1 not found")
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        "-NewInstance",
        "-NoBrowser",
        "-StartAfterPort",
        str(current_port),
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
        env=os.environ.copy(),
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "start_run_desk.ps1 failed").strip())
    match = re.search(r"Run Desk ready:\s+(http://127\.0\.0\.1:(\d+)/)", proc.stdout or "")
    url = match.group(1) if match else None
    port = int(match.group(2)) if match else None
    return {
        "ok": True,
        "launcher": "start_run_desk.ps1",
        "port": port,
        "url": url,
        "stdout": proc.stdout or "",
    }


class Server(ThreadingHTTPServer):
    allow_reuse_address = False


class Handler(BaseHTTPRequestHandler):
    server_version = "CockpitRunDesk/1.0"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, obj: dict, status: int = 200) -> None:
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path
        query = parse_qs(parsed.query)

        if route == "/":
            if not INDEX_HTML.is_file():
                self._send_bytes(b"Missing webui/index.html", "text/plain", 500)
                return
            self._send_bytes(INDEX_HTML.read_bytes(), "text/html; charset=utf-8")
            return

        if route == "/api/analyses":
            self._send_json(_public_registry())
            return

        if route == "/api/reports":
            pf = (query.get("project", [""])[0] or "").strip() or None
            self._send_json(_list_reports(pf))
            return

        if route == "/api/dashboard":
            pf = (query.get("project", [""])[0] or "").strip() or None
            self._send_json(_dashboard_payload(pf))
            return

        if route == "/artifact":
            self._serve_artifact(query)
            return

        if route == "/artifact/view":
            self._serve_artifact_view(query)
            return

        if route.startswith("/assets/"):
            self._serve_asset(route[len("/assets/"):])
            return

        self._send_bytes(b"Not found", "text/plain", 404)

    def _serve_asset(self, rel_path: str) -> None:
        rel = rel_path.strip().lstrip("/")
        if not rel or ".." in rel.replace("\\", "/").split("/"):
            self._send_bytes(b"Forbidden", "text/plain", 403)
            return
        candidate = (WEB_ASSETS_ROOT / rel).resolve()
        try:
            candidate.relative_to(WEB_ASSETS_ROOT)
        except ValueError:
            self._send_bytes(b"Forbidden", "text/plain", 403)
            return
        if candidate.is_file():
            ctype = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            self._send_bytes(candidate.read_bytes(), ctype)
            return
        self._send_bytes(b"Not found", "text/plain", 404)

    def _serve_artifact(self, query: dict) -> None:
        project_id = (query.get("project", [""])[0]).strip()
        rel = (query.get("path", [""])[0]).strip()
        if not project_id or not rel:
            self._send_bytes(b"Missing project or path", "text/plain", 400)
            return
        candidate = _resolve_artifact_path(project_id, rel)
        if not candidate:
            self._send_bytes(b"Not found", "text/plain", 404)
            return
        ctype = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self._send_bytes(candidate.read_bytes(), ctype)

    def _serve_artifact_view(self, query: dict) -> None:
        project_id = (query.get("project", [""])[0]).strip()
        rel = (query.get("path", [""])[0]).strip()
        if not project_id or not rel:
            self._send_bytes(b"Missing project or path", "text/plain", 400)
            return
        candidate = _resolve_artifact_path(project_id, rel)
        if not candidate:
            self._send_bytes(b"Not found", "text/plain", 404)
            return
        html_companion = _companion_html_path(candidate)
        if html_companion and html_companion.is_file():
            candidate = html_companion
            body = html_companion.read_bytes()
        else:
            rendered = _render_artifact_html(project_id, candidate)
            if not rendered:
                self._send_bytes(b"Could not render report", "text/plain", 500)
                return
            body = rendered
        self._send_bytes(body, "text/html; charset=utf-8")

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/server/run":
            if not _check_token(self.headers):
                self._send_json({"ok": False, "error": "unauthorized"}, 401)
                return
            try:
                current_port = int(self.server.server_address[1])
                self._send_json(_launch_server_py(current_port))
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return

        if route != "/api/run":
            self._send_bytes(b"Not found", "text/plain", 404)
            return

        if not _check_token(self.headers):
            self._send_json({"ok": False, "error": "unauthorized"}, 401)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            self._send_json({"ok": False, "error": "invalid JSON body"}, 400)
            return

        aid = str(data.get("id", ""))
        pid = str(data.get("project_id", ""))
        key = f"{pid}:{aid}" if pid else aid
        analysis = _ANALYSES_BY_KEY.get(key)
        if not analysis and pid:
            analysis = next((a for a in ANALYSES if a["id"] == aid), None)
        if not analysis:
            self._send_json({"ok": False, "error": "unknown analysis id"}, 400)
            return

        params = data.get("params") or {}
        if not isinstance(params, dict):
            self._send_json({"ok": False, "error": "params must be an object"}, 400)
            return

        argv, err = _build_argv(analysis, params)
        if err:
            self._send_json({"ok": False, "error": err}, 400)
            return

        project_root = Path(analysis["project_root"])
        timeout = int(os.environ.get("ANALYSIS_RUN_TIMEOUT_SEC", "7200"))
        try:
            proc = subprocess.run(
                argv,
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as e:
            self._send_json({
                "ok": False,
                "exit_code": -1,
                "stdout": e.stdout or "",
                "stderr": (e.stderr or "") + f"\nProcess exceeded {timeout}s timeout.",
                "error": "timeout",
            })
            return

        artifact_url, artifact_kind = (None, None)
        secondary_artifacts: list[dict] = []
        pdf_stdout, pdf_stderr = "", ""
        if proc.returncode == 0:
            post = analysis.get("post_run") or {}
            if post.get("type") == "funnel_narrative_pdf":
                artifact_url, artifact_kind, pdf_stdout, pdf_stderr = _run_funnel_narrative_pdf(
                    analysis, params
                )
            if not artifact_url:
                artifact_url, artifact_kind = _resolve_artifact(analysis, params)
            secondary_artifacts = _resolve_secondary_artifacts(analysis, params)

        stderr = proc.stderr or ""
        if pdf_stderr:
            stderr = stderr + ("\n" if stderr else "") + pdf_stderr
        stdout = proc.stdout or ""
        if pdf_stdout:
            stdout = stdout + ("\n" if stdout else "") + pdf_stdout

        self._send_json({
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "artifact_url": artifact_url,
            "artifact_kind": artifact_kind,
            "secondary_artifacts": secondary_artifacts,
        })


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Cockpit Run Desk")
    parser.add_argument("--open", action="store_true", help="Open browser on start")
    parser.add_argument("--port", type=int, default=None, help="Listen port")
    args = parser.parse_args()

    port = args.port if args.port is not None else int(os.environ.get("ANALYSIS_WEB_PORT", "8765"))
    url = f"http://127.0.0.1:{port}/"
    try:
        httpd = Server(("127.0.0.1", port), Handler)
    except OSError as e:
        sys.exit(
            f"Could not bind 127.0.0.1:{port} ({e}).\n"
            f"Set ANALYSIS_WEB_PORT to another port, e.g. 8771."
        )
    print(f"Cockpit Run Desk: {url} (registry v{REGISTRY_VERSION}, {len(ANALYSES)} jobs)")
    open_browser = args.open or os.environ.get("ANALYSIS_WEB_OPEN_BROWSER", "") == "1"
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.shutdown()


if __name__ == "__main__":
    main()
