import json

WARNING = "Review before sharing: this report may contain hostname and local technical information."


def build_report(incident, system=None, network=None, version="1.0.0"):
    return {
        "warning": WARNING,
        "app_version": version,
        "component_versions": {"backend": "1.0.0"},
        "incident": incident,
        "system": system,
        "network": network,
        "known_limitations": ["Local-only MVP", "No MDM integration", "macOS not tested"],
    }


def to_markdown(r):
    i = r["incident"]
    lines = [
        "# EDST Incident Report",
        f"> {r['warning']}",
        "",
        f"- App version: {r['app_version']}",
        f"- Incident: #{i['id']} {i['title']}",
        f"- Status: {i['status']}",
        f"- Priority: {i['priority']}",
        "",
        "## Description",
        i["description"],
        "",
        "## Troubleshooting Notes",
    ]
    for n in i.get("notes", []):
        lines += [f"- **{n['timestamp']}** — {n['action']} → {n['result']} Next: {n['next_step']}"]
    lines += ["", "## Known Limitations"] + [f"- {x}" for x in r["known_limitations"]]
    return "\n".join(lines)


def to_json(r):
    return json.dumps(r, indent=2, default=str)
