# AI Remove Background GIMP3 Plugin

This GIMP plugin allows users to remove image backgrounds using AI-powered tools like [rembg](https://github.com/danielgatis/rembg). The plugin integrates with GIMP3 to offer a simple way to remove backgrounds. It can process a single image in GIMP.

## Features

- **AI-Powered Background Removal:** Removes the background using the `rembg` tool, an AI-powered background removal library.
- **Multiple AI Models:** Choose from various models like u2net, isnet-general-use, sam, and more.
- **Simple Integration:** Works seamlessly within GIMP's interface.

## Requirements

- **GIMP 3.0+** (available via Flatpak or native package)
- **Python 3.11+** (Python 3.13 recommended for compatibility with rembg)
- **rembg 2.0+** Python library

## Installation on Debian

### For Flatpak GIMP (Recommended for GIMP 3.0+)

#### 1. Install GIMP via Flatpak (if not already installed)
```bash
sudo apt update
sudo apt install flatpak
sudo flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
sudo apt install gnome-software-plugin-flatpak
sudo reboot

flatpak install flathub org.gimp.GIMP

# Verify installation
flatpak list | grep gimp
flatpak run org.gimp.GIMP --version
```

#### 2. Download and Install the Plugin
```bash
# Create plugin directory
mkdir -p ~/.config/GIMP/3.0/plug-ins/
cd ~/.config/GIMP/3.0/plug-ins/

# Download and extract the plugin
curl -L -o /tmp/gimp3-plugin.zip https://github.com/ismdevteam/gimp3-rembg-plugin/archive/refs/heads/main.zip
unzip -q /tmp/gimp3-plugin.zip
mv gimp3-rembg-plugin-main gimp3-rembg-plugin
rm /tmp/gimp3-plugin.zip

# Make the plugin executable
chmod +x gimp3-rembg-plugin/gimp3-rembg-plugin.py

# Verify files
ls -la gimp3-rembg-plugin/
```

#### 3. Install rembg Dependencies
```bash
# Enter GIMP Flatpak environment
flatpak run --command=bash org.gimp.GIMP
python3 -m ensurepip --upgrade

# Choose ONE of the following based on your hardware:

# Option 1: For CPU processing (works on all systems)
python3 -m pip install "rembg[cpu]"

# Option 2: For NVIDIA GPU acceleration (requires CUDA-compatible GPU)
# python3 -m pip install "rembg[gpu]"

exit
```

#### 4. Launch GIMP
```bash
flatpak run org.gimp.GIMP
```

### For Native GIMP (APT Installation on Debian 13+)

If you have GIMP 3.0+ installed via APT (available on Debian 13+):

```bash
# Check if GIMP 3.0+ is available
apt-cache policy gimp
# To use gimp3-rembg-plugin, GIMP version must be > 3.0.0 in the result

# Install GIMP and Python pip
sudo apt install gimp python3-pip

# Note: python3-gi, python3-gi-cairo, and gir1.2-gtk-3.0 are automatically installed as dependencies

# Choose ONE of the following based on your hardware:

# Option 1: For CPU processing (works on all systems)
python3 -m pip install --user "rembg[cpu]" --break-system-packages

# Option 2: For NVIDIA GPU acceleration (requires CUDA-compatible GPU)
# python3 -m pip install --user "rembg[gpu]" --break-system-packages

# Install plugin (same location as Flatpak)
mkdir -p ~/.config/GIMP/3.0/plug-ins/
cd ~/.config/GIMP/3.0/plug-ins/
curl -L -o /tmp/gimp3-plugin.zip https://github.com/ismdevteam/gimp3-rembg-plugin/archive/refs/heads/main.zip
unzip -q /tmp/gimp3-plugin.zip
mv gimp3-rembg-plugin-main gimp3-rembg-plugin
chmod +x gimp3-rembg-plugin/gimp3-rembg-plugin.py

# Launch GIMP
gimp
```

**Important:** On Debian 13+, you must use `--break-system-packages` flag with pip due to Python's externally-managed environment protection (PEP 668).

## Usage

1. **Open GIMP** and load an image.
2. Go to **Filters → Development → ISM Tools AI Filters → AI Remove Background...**
3. Configure the options:
   - **Model:** Choose which AI model to use for background removal (default: u2net).
4. Click **OK** to run the plugin.

## First Run Notes

On the first run with a new model:
- The AI model files will be downloaded automatically (approximately 176MB for u2net)
- This may take a few minutes depending on your internet connection
- Files are saved to:
  - Flatpak: `~/.var/app/org.gimp.GIMP/data/.u2net/`
  - Native: `~/.u2net/`
- Subsequent runs will be faster as models are cached locally

Example download progress:
```
Downloading data from 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx' to file '/home/user/.var/app/org.gimp.GIMP/data/.u2net/u2net.onnx'.
100%|████████████████████████████████| 176M/176M [00:00<00:00, 254GB/s]
```

## Available Models

The plugin supports all models available in rembg 2.0+, including:
- `u2net` (default) - General purpose model
- `u2netp` - Lightweight version of u2net
- `isnet-general-use` - High quality general segmentation
- `isnet-anime` - Optimized for anime/manga images
- `sam` - Segment Anything Model (requires specific prompts)
- `birefnet-general` - Advanced general purpose model
- `bria-rmbg` - State-of-the-art model by BRIA AI

## Troubleshooting

### Plugin doesn't appear in menu
- Verify the plugin is in `~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin/`
- Ensure `gimp3-rembg-plugin.py` is executable (`chmod +x`)
- Restart GIMP completely

### "ModuleNotFoundError: No module named 'rembg'"
- Ensure you installed rembg inside the Flatpak environment (Step 3 for Flatpak installation)
- For native GIMP, ensure rembg is installed with `--break-system-packages` flag

### First model download fails
- Ensure network connectivity
- Check disk space in your home directory

### Processing is slow
- The CPU backend is slower. If you have a compatible NVIDIA GPU, use `rembg[gpu]` instead of `rembg[cpu]`
- Larger images take more time. Consider resizing very large images first

## Contributing

Feel free to open issues or submit pull requests to improve this plugin! Contributions are always welcome.

## License

This project is licensed under the **GPLv3** License - see the LICENSE file for details.

## Acknowledgments

- **rembg**: This plugin integrates with [rembg](https://github.com/danielgatis/rembg) to handle AI-powered background removal.
- **GIMP**: The GNU Image Manipulation Program, a free and open-source image editor.
- **All AI model contributors**: For making their models available for public use.
