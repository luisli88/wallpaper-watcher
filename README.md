# Wallpaper Background Watcher

A background service that monitors your clipboard for image URLs and automatically downloads them to organized folders based on resolution.

## Features

- Monitors clipboard for image URLs in real-time
- Validates URLs against configured trusted domains
- Automatically downloads images
- Organizes images by resolution into configurable folders (4K, wide, HD)
- Preserves original filenames from URLs
- Runs continuously in the background

## Requirements

- Python 3.13+
- Wayland (uses `wl-paste` for clipboard access)
- ImageMagick (uses `identify` for resolution detection)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd looknfeel
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the application by editing `config.yml`:
```yaml
bg_watcher:
  root_folder: ~/Pictures/Wallpapers
  allowed_domains:
  - i.imgur.com
  - wallhaven.cc
  size_breakpoints:
  - name: 4k
    min_width: 3840
    min_height: 2160
    folder: 4K
  - name: wide
    min_width: 2560
    min_height: 1080
    folder: wide
  - name: hd
    folder: HD
```

## Configuration

### root_folder
Base directory where wallpapers will be saved. Supports `~` for home directory.

### allowed_domains
List of trusted domains. Only URLs from these domains will be processed.

### size_breakpoints
Define resolution thresholds and corresponding folders. Images are matched to the first bucket whose `min_width` and `min_height` are satisfied. The HD bucket with `min_width: 0` and `min_height: 0` acts as a catch-all default.

## Usage

Run the watcher:
```bash
python bg_watcher.py
```

The script will:
1. Monitor your clipboard continuously
2. Detect when a URL is copied
3. Validate the URL domain
4. Download the image
5. Detect its resolution
6. Save it to the appropriate folder with its original filename

### Running as a background service

To run on system startup with uwsm-app, create a service file or add to your window manager's autostart.

## Example

Copy an image URL like `https://i.imgur.com/example.jpg` to your clipboard. The watcher will:
- Download the image
- Check its resolution (e.g., 3840x2160)
- Save it as `~/Pictures/Wallpapers/4K/example.jpg`
- Log: `Saved image example.jpg to /home/user/Pictures/Wallpapers/4K (resolution: 3840x2160)`

## License

MIT
