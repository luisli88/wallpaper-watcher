# Wallpaper Background Watcher

A background service that monitors your clipboard for image URLs and automatically downloads them to organized folders based on resolution.

## Features

- Monitors clipboard for image URLs in real-time
- Validates URLs against configured trusted domains
- Automatically downloads images
- Organizes images by resolution into configurable folders (4K, wide, HD)
- Creates symlinks to higher resolution images in lower resolution folders for compatibility
- Preserves original filenames from URLs
- Runs continuously in the background

## Requirements

- Python 3.13+
- Wayland (uses `wl-paste` for clipboard access)
- ImageMagick (uses `identify` for resolution detection)

## Project Structure

```
wallpaper-watcher/
├── lib/
│   └── bg_watcher.py     # Main Python script
├── config.yml            # Configuration file
├── requirements.txt      # Python dependencies
├── setup.sh             # Virtual environment setup
├── run.sh               # Execution script
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/wallpaper-watcher.git
cd wallpaper-watcher
```

2. Configure the application by editing `config.yml`:
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

**Note:** Higher resolution images are automatically made available to lower resolution folders via symbolic links. For example, a 4K image saved to the 4K folder will also have symlinks created in the wide and HD folders. This allows smaller screens to access higher quality images while preventing larger screens from accessing lower quality images.

## Usage

### Quick Start

Simply run the provided script:
```bash
./run.sh
```

This script will automatically:
- Check if the virtual environment exists (creates it if needed)
- Install or update dependencies
- Start the wallpaper watcher

### Manual Setup (Optional)

If you prefer to set up manually:
```bash
./setup.sh                    # Create venv and install dependencies
.venv/bin/python lib/bg_watcher.py  # Run directly
```

### What the watcher does

The script will:
1. Monitor your clipboard continuously
2. Detect when a URL is copied
3. Validate the URL domain
4. Download the image
5. Detect its resolution
6. Save it to the appropriate folder with its original filename

### Running as a background service

#### Hyprland with uwsm

Add the following to your Hyprland config (`~/.config/hypr/hyprland.conf`):

```conf
exec-once = uwsm-app -- /absolute/path/to/wallpaper-watcher/run.sh
```

Replace `/absolute/path/to/wallpaper-watcher` with the actual absolute path where you cloned the repository.

**Example:**
```conf
exec-once = uwsm-app -- ~/projects/wallpaper-watcher/run.sh
```

The `uwsm-app` wrapper ensures proper integration with the Wayland session manager.

#### Other window managers

For other setups, add to your autostart configuration:

```bash
/absolute/path/to/wallpaper-watcher/run.sh &
```

The script handles all setup automatically, making it ideal for autostart scenarios.

## Example

Copy an image URL like `https://i.imgur.com/example.jpg` to your clipboard. The watcher will:
- Download the image
- Check its resolution (e.g., 3840x2160)
- Save it as `~/Pictures/Wallpapers/4K/example.jpg`
- Create symlinks in `~/Pictures/Wallpapers/wide/example.jpg` and `~/Pictures/Wallpapers/HD/example.jpg`
- Log: `Saved image example.jpg to ~/.../Wallpapers/4K (resolution: 3840x2160)`
- Log: `Symlinks created in lower resolution folders for broader compatibility`

## License

MIT
