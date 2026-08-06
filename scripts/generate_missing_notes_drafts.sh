#!/usr/bin/env bash
set -euo pipefail

STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_DIR="_doc_discovery_output/missing_notes_drafts_${STAMP}"
DRAFT_DIR="$OUT_DIR/drafts"
REPORT="$OUT_DIR/missing_notes_drafts_report.md"
ZIP="$OUT_DIR.zip"

mkdir -p "$DRAFT_DIR"
: > "$REPORT"

python3 - <<'PY' "$OUT_DIR" "$DRAFT_DIR" "$REPORT"
from pathlib import Path
import re
import sys
from datetime import datetime

out_dir = Path(sys.argv[1])
draft_dir = Path(sys.argv[2])
report = Path(sys.argv[3])

registry_path = Path("airflow/config/scraper_registry.yaml")
scrapers_root = Path("src/scrapers")

def write_report(text=""):
    with report.open("a", encoding="utf-8") as f:
        f.write(text + "\n")

def module_to_path(module: str) -> Path:
    return scrapers_root / Path(*module.split("."))

def case_insensitive_match(path):
    if path.exists():
        return path
    target = str(path).lower()
    for p in scrapers_root.rglob("*"):
        if p.is_dir() and str(p).lower() == target:
            return p
    return None

def parse_registry():
    if not registry_path.exists():
        raise SystemExit(f"Registry not found: {registry_path}")

    entries = []
    current = None

    for line_no, raw in enumerate(registry_path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw.strip()

        if not stripped or stripped.startswith("#"):
            continue

        m_id = re.match(r"-\s*scraper_id:\s*([A-Za-z0-9_\-]+)", stripped)
        if m_id:
            if current:
                entries.append(current)
            current = {"scraper_id": m_id.group(1), "line": line_no}
            continue

        if current:
            m = re.match(r"(module|schedule|depends_on|tags):\s*(.+)", stripped)
            if m:
                current[m.group(1)] = m.group(2).strip().strip('"').strip("'")

    if current:
        entries.append(current)

    return [e for e in entries if "scraper_id" in e and "module" in e]

def extract_urls(text: str):
    urls = sorted(set(re.findall(r"https?://[^\s\"')<>]+", text)))
    return urls[:20]

def extract_imports(text: str):
    imports = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            imports.append(s)
    return sorted(set(imports))[:40]

def extract_defs(text: str):
    defs = []
    for line in text.splitlines():
        m = re.match(r"\s*(class|def)\s+([A-Za-z_][A-Za-z0-9_]*)", line)
        if m:
            defs.append(f"{m.group(1)} {m.group(2)}")
    return defs[:60]

def grep_lines(text: str, patterns):
    out = []
    for i, line in enumerate(text.splitlines(), start=1):
        if any(re.search(p, line, flags=re.IGNORECASE) for p in patterns):
            out.append(f"L{i}: {line.strip()}")
    return out[:80]

def inspect_scraper(path: Path):
    py_files = sorted(path.glob("*.py"))
    req = path / "requirements.txt"
    dockerfile = path / "Dockerfile"
    readme = path / "README.md"

    combined = ""
    for py in py_files:
        try:
            combined += f"\n\n# FILE: {py.name}\n"
            combined += py.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            combined += f"\n\n# FILE: {py.name}\n[ERROR READING FILE: {e}]"

    return {
        "py_files": py_files,
        "has_requirements": req.exists(),
        "requirements_empty": req.exists() and req.stat().st_size == 0,
        "requirements_text": req.read_text(encoding="utf-8", errors="replace") if req.exists() else "",
        "has_dockerfile": dockerfile.exists(),
        "has_readme": readme.exists(),
        "urls": extract_urls(combined),
        "imports": extract_imports(combined),
        "defs": extract_defs(combined),
        "todo_lines": grep_lines(combined, [r"TODO", r"TBD", r"FIXME", r"pass$", r"NotImplemented", r"placeholder", r"stub"]),
        "risk_lines": grep_lines(combined, [r"verify=False", r"403", r"Forbidden", r"minio", r"dagu", r"password", r"secret", r"token", r"api_key", r"host\.docker\.internal"]),
        "output_lines": grep_lines(combined, [r"raw", r"processed", r"upload", r"download", r"json", r"csv", r"xml", r"html"]),
    }

def provider_title(scraper_id, module):
    return scraper_id.replace("_", " ").title()

def draft_note(entry, path: Path, info):
    scraper_id = entry["scraper_id"]
    module = entry["module"]
    title = provider_title(scraper_id, module)

    lines = []
    lines.append(f"# {title} Scraper Notes")
    lines.append("")
    lines.append("Status: Draft generated from current repo evidence.")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    lines.append(f"- Scraper ID: `{scraper_id}`")
    lines.append(f"- Module: `{module}`")
    lines.append(f"- Schedule: `{entry.get('schedule', 'Unknown — evidence needed')}`")
    if "depends_on" in entry:
        lines.append(f"- Depends on: `{entry['depends_on']}`")
    if "tags" in entry:
        lines.append(f"- Tags: `{entry['tags']}`")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- Scraper folder: `{path}`")
    lines.append(f"- Python files: {', '.join(f'`{p.name}`' for p in info['py_files']) if info['py_files'] else 'Unknown — evidence needed'}")
    lines.append(f"- Dockerfile present: {'Yes' if info['has_dockerfile'] else 'No'}")
    lines.append(f"- requirements.txt present: {'Yes' if info['has_requirements'] else 'No'}")
    if info["has_requirements"]:
        lines.append(f"- requirements.txt empty: {'Yes' if info['requirements_empty'] else 'No'}")
    lines.append("")
    lines.append("## Source / endpoint evidence")
    lines.append("")
    if info["urls"]:
        for url in info["urls"]:
            lines.append(f"- `{url}`")
    else:
        lines.append("- Unknown — no URL literal found in the inspected Python files.")
    lines.append("")
    lines.append("## Observed implementation shape")
    lines.append("")
    if info["defs"]:
        for d in info["defs"]:
            lines.append(f"- `{d}`")
    else:
        lines.append("- Unknown — no class/function definitions found in inspected Python files.")
    lines.append("")
    lines.append("## Imports / dependencies observed")
    lines.append("")
    if info["imports"]:
        for imp in info["imports"]:
            lines.append(f"- `{imp}`")
    else:
        lines.append("- Unknown — no imports found in inspected Python files.")
    lines.append("")
    lines.append("## Output behavior")
    lines.append("")
    if info["output_lines"]:
        lines.append("Observed output-related lines from code inspection:")
        lines.append("")
        for l in info["output_lines"][:25]:
            lines.append(f"- `{l}`")
    else:
        lines.append("- Unknown — output behavior needs direct code review.")
    lines.append("")
    lines.append("Use neutral wording such as `observed output shape`, `processed provider-specific output`, and `current output behavior` unless direct evidence proves a stronger claim.")
    lines.append("")
    lines.append("## Known risks / review notes")
    lines.append("")
    if info["risk_lines"]:
        for l in info["risk_lines"]:
            lines.append(f"- `{l}`")
    else:
        lines.append("- No obvious risk keywords found by static scan.")
    if not info["has_dockerfile"]:
        lines.append("- Dockerfile is not present in this scraper folder. Confirm whether this is expected because Dockerfiles may be generated.")
    if not info["has_requirements"]:
        lines.append("- requirements.txt is missing. Confirm whether dependencies are inherited or this is a packaging gap.")
    if info["requirements_empty"]:
        lines.append("- requirements.txt exists but is empty. Confirm whether this scraper actually has no external dependencies.")
    lines.append("")
    lines.append("## TODO / incomplete markers")
    lines.append("")
    if info["todo_lines"]:
        for l in info["todo_lines"]:
            lines.append(f"- `{l}`")
    else:
        lines.append("- No TODO/TBD/FIXME/pass markers found by static scan.")
    lines.append("")
    lines.append("## Runtime status")
    lines.append("")
    lines.append("- Unknown — evidence needed unless a runtime validation report exists for this scraper.")
    lines.append("")
    lines.append("## Documentation status")
    lines.append("")
    lines.append("- This note is a generated draft and needs human review before being committed.")
    lines.append("- Verify endpoint behavior, runtime output, and any provider-specific assumptions before treating this as final documentation.")
    lines.append("")

    return "\n".join(lines)

entries = parse_registry()

missing = []
for entry in entries:
    expected = module_to_path(entry["module"])
    actual = case_insensitive_match(expected)
    if actual is None:
        missing.append((entry, expected, None, "folder_missing"))
        continue
    if not (actual / "notes.md").exists():
        missing.append((entry, expected, actual, "notes_missing"))

write_report("# Missing Active Scraper Notes Draft Report")
write_report("")
write_report(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
write_report("")
write_report("Purpose: draft-only notes generation for active registry scrapers missing `notes.md`.")
write_report("")
write_report("No files under `src/scrapers` were modified.")
write_report("")
write_report(f"Active registry entries parsed: {len(entries)}")
write_report(f"Active entries missing notes.md or folder evidence: {len(missing)}")
write_report("")
write_report("## Missing notes inventory")
write_report("")
write_report("| Scraper ID | Module | Expected folder | Actual folder | Status | Draft file |")
write_report("|---|---|---|---|---|---|")

copy_lines = []
for entry, expected, actual, status in missing:
    scraper_id = entry["scraper_id"]
    module = entry["module"]
    safe_name = scraper_id.replace("/", "_")
    draft_path = draft_dir / f"{safe_name}.notes.md"

    if actual is not None:
        info = inspect_scraper(actual)
        draft_path.write_text(draft_note(entry, actual, info), encoding="utf-8")
        actual_s = f"`{actual}`"
        copy_lines.append((draft_path, actual / "notes.md"))
    else:
        draft_path.write_text(
            f"# {provider_title(scraper_id, module)} Scraper Notes\n\n"
            "Status: Draft placeholder only.\n\n"
            f"- Scraper ID: `{scraper_id}`\n"
            f"- Module: `{module}`\n"
            f"- Expected folder: `{expected}`\n"
            "- Status: Unknown — expected scraper folder was not found.\n",
            encoding="utf-8",
        )
        actual_s = "Unknown — folder not found"

    write_report(f"| `{scraper_id}` | `{module}` | `{expected}` | {actual_s} | `{status}` | `{draft_path}` |")

apply_script = out_dir / "apply_reviewed_notes.sh"
with apply_script.open("w", encoding="utf-8") as f:
    f.write("#!/usr/bin/env bash\n")
    f.write("set -euo pipefail\n")
    f.write("\n")
    f.write("# Review drafts before running this script.\n")
    f.write("# This copies generated notes into scraper folders only when notes.md is still missing.\n")
    f.write("\n")
    for src, dest in copy_lines:
        f.write(f'if [ ! -f "{dest}" ]; then cp "{src}" "{dest}"; else echo "SKIP existing {dest}"; fi\n')

apply_script.chmod(0o755)

write_report("")
write_report("## Apply script")
write_report("")
write_report(f"After manual review, run: `{apply_script}`")
write_report("")
write_report("Do not run the apply script until the drafts have been reviewed.")
PY

zip -r "$ZIP" "$OUT_DIR" >/dev/null

echo "Created:"
echo "  $REPORT"
echo "  $ZIP"
