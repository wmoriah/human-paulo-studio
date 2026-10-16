#!/usr/bin/env python3
"""
Media Inspector & Preparation Helper for Human Paulo Studio Skills.
- Converts iPhone .HEIC/.WEBP images to standard .jpg/.png (via macOS sips or ffmpeg).
- Inspects audio/video duration, resolution, and streams via ffprobe.
- Trims dead start/end segments of videos via ffmpeg without re-encoding or with clean AAC/H264.
- Extracts representative frames from videos for visual VFX inspection.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe_media(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration,size,format_name",
        "-show_entries",
        "stream=index,codec_type,codec_name,width,height,sample_rate,channels,duration",
        "-of",
        "json",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {"error": res.stderr.strip(), "path": str(path)}
    data = json.loads(res.stdout)
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    duration = float(fmt.get("duration", 0.0) or 0.0)
    return {
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
        "duration_seconds": round(duration, 2),
        "size_bytes": int(fmt.get("size", 0) or 0),
        "format_name": fmt.get("format_name", ""),
        "streams": streams,
    }


def convert_image(path: Path, out_dir: Path, target_ext: str = "jpg") -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{path.stem}.{target_ext.lstrip('.')}"
    if shutil.which("sips") and path.suffix.lower() in {".heic", ".heif", ".tif", ".tiff"}:
        fmt = "jpeg" if target_ext in {"jpg", "jpeg"} else "png"
        res = subprocess.run(
            ["sips", "-s", "format", fmt, str(path), "--out", str(out_path)],
            capture_output=True,
            text=True,
        )
        if res.returncode == 0 and out_path.exists():
            return {"status": "ok", "input": str(path), "output": str(out_path.resolve())}
    res = subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), str(out_path)],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return {"status": "error", "error": res.stderr.strip()}
    return {"status": "ok", "input": str(path), "output": str(out_path.resolve())}


def trim_media(path: Path, out_path: Path, start: float, end: float = None) -> dict:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-y", "-ss", str(start)]
    if end is not None and end > start:
        cmd.extend(["-to", str(end)])
    cmd.extend(["-i", str(path), "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", str(out_path)])
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {"status": "error", "error": res.stderr.strip()}
    return {"status": "ok", "output": str(out_path.resolve()), "probe": probe_media(out_path)}


def extract_frames(path: Path, out_dir: Path, count: int = 6) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    info = probe_media(path)
    duration = info.get("duration_seconds", 0.0)
    if duration <= 0:
        return {"status": "error", "error": "Could not determine video duration"}
    fps = max(count / duration, 0.2)
    pattern = out_dir / "frame_%02d.jpg"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(path),
        "-vf",
        f"fps={fps:.4f},scale=640:-1",
        "-frames:v",
        str(count),
        str(pattern),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return {"status": "error", "error": res.stderr.strip()}
    frames = [str(p.resolve()) for p in sorted(out_dir.glob("frame_*.jpg"))]
    return {"status": "ok", "duration_seconds": duration, "frames": frames}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe", help="Inspect audio/video/image file via ffprobe")
    p_probe.add_argument("file", type=Path)

    p_conv = sub.add_parser("convert-image", help="Convert HEIC/WEBP image to JPG/PNG")
    p_conv.add_argument("file", type=Path)
    p_conv.add_argument("--out-dir", type=Path, required=True)
    p_conv.add_argument("--ext", default="jpg", choices=("jpg", "png"))

    p_trim = sub.add_parser("trim", help="Trim dead start/end from video or audio")
    p_trim.add_argument("file", type=Path)
    p_trim.add_argument("--out", type=Path, required=True)
    p_trim.add_argument("--start", type=float, default=0.0)
    p_trim.add_argument("--end", type=float, default=None)

    p_frames = sub.add_parser("extract-frames", help="Extract keyframes from video for VFX analysis")
    p_frames.add_argument("file", type=Path)
    p_frames.add_argument("--out-dir", type=Path, required=True)
    p_frames.add_argument("--count", type=int, default=6)

    args = parser.parse_args()
    if args.command == "probe":
        out = probe_media(args.file)
    elif args.command == "convert-image":
        out = convert_image(args.file, args.out_dir, args.ext)
    elif args.command == "trim":
        out = trim_media(args.file, args.out, args.start, args.end)
    elif args.command == "extract-frames":
        out = extract_frames(args.file, args.out_dir, args.count)
    else:
        sys.exit(1)

    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
