#!/usr/bin/env python3
import os
import shutil
import subprocess
import time
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen, Request


@dataclass
class SizeBucket:
    name: str
    min_width: int
    min_height: int
    folder: Path


def parse_simple_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    if not config_path.exists():
        return {"allowed_domains": [], "size_breakpoints": []}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        bg_config = data.get("bg_watcher", {})
        return {
            "allowed_domains": bg_config.get("allowed_domains", []),
            "size_breakpoints": bg_config.get("size_breakpoints", []),
            "root_folder": bg_config.get("root_folder", ""),
        }
    except Exception:
        return {"allowed_domains": [], "size_breakpoints": [], "root_folder": ""}


def load_allowed_domains(config_path: Path) -> List[str]:
    cfg = parse_simple_config(config_path)
    return cfg.get("allowed_domains", [])


def load_size_buckets(config_path: Path) -> List[SizeBucket]:
    cfg = parse_simple_config(config_path)
    raw_sizes = cfg.get("size_breakpoints", [])

    # Get root folder from config or use default
    root_folder_str = cfg.get("root_folder", "").strip()
    if root_folder_str:
        root_folder = Path(root_folder_str).expanduser()
    else:
        root_folder = Path.home() / "Pictures" / "Wallpapers"

    buckets: List[SizeBucket] = []
    for item in raw_sizes:
        try:
            name = str(item.get("name", "")).strip() or "custom"
            min_width = int(item.get("min_width", 0))
            min_height = int(item.get("min_height", 0))
            folder_name = str(item.get("folder", name)).strip() or name
            folder_path = root_folder / folder_name
            buckets.append(SizeBucket(name, min_width, min_height, folder_path))
        except Exception:
            continue

    # Always ensure HD default bucket exists at the end
    hd_exists = any(b.name.lower() == "hd" for b in buckets)
    if not hd_exists:
        hd_folder = root_folder / "HD"
        buckets.append(SizeBucket("hd", 0, 0, hd_folder))

    # Ensure folders exist
    for b in buckets:
        b.folder.mkdir(parents=True, exist_ok=True)

    return buckets


def get_clipboard_text() -> str:
    """Read text from the Wayland clipboard using wl-paste."""
    try:
        result = subprocess.run(
            ["wl-paste", "--type", "text"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def is_url(value: str) -> bool:
    """Return True if the value looks like an HTTP or HTTPS URL."""
    try:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def domain_allowed(url: str, allowed_domains: Iterable[str]) -> bool:
    """Return True when the URL's netloc ends with one of the allowed domains."""
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    for domain in allowed_domains:
        d = domain.lower()
        if host == d or host.endswith(f".{d}"):
            return True
    return False


def download_image(url: str, target_dir: Path) -> Optional[Path]:
    """Download image to a temporary file under target_dir; return its path."""
    target_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = target_dir / f"tmp_{os.getpid()}_{int(time.time())}.img"
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=10) as resp:  # nosec - trusted domains filtered
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type:
                return None
            data = resp.read()
            tmp_path.write_bytes(data)
        return tmp_path
    except Exception as e:
        print(e.__str__())
        return None


def get_image_resolution(path: Path) -> str:
    """Get WxH resolution using ImageMagick identify."""
    try:
        result = subprocess.run(
            ["identify", "-format", "%wx%h", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def parse_resolution(resolution: str) -> Optional[tuple[int, int]]:
    """Parse a WxH string into ints; return None if invalid."""
    if not resolution or "x" not in resolution:
        return None
    try:
        w_str, h_str = resolution.lower().split("x", 1)
        return int(w_str), int(h_str)
    except Exception:
        return None


def choose_destination(resolution: str, buckets: List[SizeBucket]) -> Path:
    """Pick first bucket whose min_width/height are satisfied by the resolution, defaulting to HD."""
    parsed = parse_resolution(resolution)
    if not parsed:
        return buckets[-1].folder

    w, h = parsed
    for bucket in buckets:
        if w >= bucket.min_width and h >= bucket.min_height:
            return bucket.folder

    # If somehow smaller than every bucket, fall back to the last one (HD by default)
    return buckets[-1].folder


def save_image(tmp_path: Path, url: str, dest_dir: Path) -> Path:
    """Move the temp file into the destination dir using the URL filename."""
    try:
        parsed = urlparse(url)
        filename = Path(parsed.path).name
        if not filename or filename == "/":
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{ts}.png"
    except Exception:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ts}.png"

    dest_path = dest_dir / filename
    # shutil.move avoids cross-device errors when /tmp lives on another filesystem
    shutil.move(str(tmp_path), dest_path)
    return dest_path


def process_clipboard(
    url: str, allowed_domains: List[str], buckets: List[SizeBucket]
) -> None:
    """Process a single clipboard URL if valid and download the image."""
    if not is_url(url):
        print(f"Clipboard content ignored (not a URL): {url}")
        return

    if not domain_allowed(url, allowed_domains):
        print(f"Clipboard URL ignored (domain not allowed): {url}")
        return

    tmp_path = download_image(url, Path("/tmp"))
    if not tmp_path:
        print(f"Failed to download or validate image from: {url}")
        return

    resolution = get_image_resolution(tmp_path)
    dest_dir = choose_destination(resolution, buckets)
    dest_path = save_image(tmp_path, url, dest_dir)
    print(f"Saved image {dest_path.name} to {dest_dir} (resolution: {resolution or 'unknown'})")


def main() -> None:
    # Config file is in the root directory (parent of lib/)
    config_path = Path(__file__).parent.parent / "config.yml"
    allowed_domains = load_allowed_domains(config_path)
    buckets = load_size_buckets(config_path)
    if not allowed_domains:
        print("No allowed domains configured; exiting.")
        return

    last_value = None
    print("bg_watcher started; monitoring clipboard for image URLs...")
    while True:
        clip_text = get_clipboard_text()
        if clip_text and clip_text != last_value:
            last_value = clip_text
            process_clipboard(clip_text, allowed_domains, buckets)
        time.sleep(1.0)


if __name__ == "__main__":
    main()
