#!/usr/bin/env python3
"""
Session & Draft Deadline Manager for Human Paulo Studio Skills.
- Tracks project stage, assets (with SHA-256), character heights, and generated prompts.
- Tracks Seedance 2.5 480p Draft jobs and enforces the 7-day 1080p upscale deadline alert.
"""
import argparse
import datetime
import json
from pathlib import Path

SEVEN_DAYS_SECONDS = 7 * 24 * 3600


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def load_session(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "project_name": path.parent.name,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "stage": "initialized",
        "ideation": {
            "discarded_cliches": [],
            "selected_concept": None,
            "devils_advocate_rounds": 0,
            "devils_advocate_notes": [],
        },
        "script_two_columns": [],
        "assets": {
            "characters": [],
            "products": [],
            "props_vehicles": [],
            "locations": [],
            "detail_closeups": [],
        },
        "storyboard": {"style_reference": None, "frames_count": 0, "approved": False},
        "draft_jobs": [],
        "outputs": [],
    }


def save_session(path: Path, data: dict) -> None:
    data["updated_at"] = now_iso()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def register_draft(path: Path, job_id: str, scene_name: str, provider: str) -> dict:
    session = load_session(path)
    created = datetime.datetime.now(datetime.timezone.utc)
    expires = created + datetime.timedelta(days=7)
    entry = {
        "job_id": job_id,
        "scene_name": scene_name,
        "provider": provider,
        "resolution": "480p_draft",
        "upgraded_to_1080p": False,
        "created_at": created.isoformat(),
        "expires_at": expires.isoformat(),
    }
    session["draft_jobs"].append(entry)
    save_session(path, session)
    return entry


def check_drafts(path: Path) -> dict:
    session = load_session(path)
    now = datetime.datetime.now(datetime.timezone.utc)
    alerts = []
    for job in session.get("draft_jobs", []):
        if job.get("upgraded_to_1080p"):
            continue
        exp = datetime.datetime.fromisoformat(job["expires_at"])
        remaining_days = (exp - now).total_seconds() / 86400.0
        status = "valid" if remaining_days > 0 else "expired_use_motion_reference_workaround"
        alerts.append({
            "job_id": job["job_id"],
            "scene_name": job["scene_name"],
            "remaining_days": round(remaining_days, 2),
            "status": status,
        })
    return {"session_file": str(path.resolve()), "stage": session.get("stage"), "draft_alerts": alerts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize or inspect session.json")
    p_init.add_argument("--file", type=Path, default=Path("work/project-session.json"))
    p_init.add_argument("--stage", type=str, default=None)

    p_draft = sub.add_parser("add-draft", help="Register a 480p Draft generation with 7-day countdown")
    p_draft.add_argument("--file", type=Path, default=Path("work/project-session.json"))
    p_draft.add_argument("--job-id", required=True)
    p_draft.add_argument("--scene", required=True)
    p_draft.add_argument("--provider", default="seedance-2.5")

    p_check = sub.add_parser("check-drafts", help="Check 7-day expiration status for 480p drafts")
    p_check.add_argument("--file", type=Path, default=Path("work/project-session.json"))

    args = parser.parse_args()
    if args.cmd == "init":
        sess = load_session(args.file)
        if args.stage:
            sess["stage"] = args.stage
        save_session(args.file, sess)
        print(json.dumps(sess, indent=2, ensure_ascii=False))
    elif args.cmd == "add-draft":
        entry = register_draft(args.file, args.job_id, args.scene, args.provider)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    elif args.cmd == "check-drafts":
        print(json.dumps(check_drafts(args.file), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
