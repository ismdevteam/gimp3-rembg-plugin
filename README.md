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

If you have GIMP 3.0+ installed via APT (available on Debian 13+), **we strongly recommend using a Python virtual environment** to install `rembg` – this avoids any risk of breaking system packages.

#### 1. Install GIMP and Python tools
```bash
sudo apt install gimp python3-pip python3-venv
```

#### 2. Create a dedicated virtual environment and install rembg
```bash
# Create the venv (choose a location, e.g. ~/.gimp3-rembg-venv)
python3 -m venv ~/.gimp3-rembg-venv

# Activate it and install rembg
source ~/.gimp3-rembg-venv/bin/activate

# Choose ONE of the following based on your hardware:

# Option 1: CPU processing (works on all systems)
pip install "rembg[cpu]"

# Option 2: NVIDIA GPU acceleration (requires CUDA-compatible GPU)
# pip install "rembg[gpu]"

deactivate
```

#### 3. Install the plugin and make it use the venv
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
```

**Now we need to tell the plugin where to find the installed `rembg` package.**  
The easiest way is to add the venv’s `site-packages` directory to Python’s search path at the very beginning of the plugin script.  
Run this command to automatically insert the correct path:

```bash
VENV_SITE=$(~/.gimp3-rembg-venv/bin/python -c "import site; print(site.getsitepackages()[0])")
sed -i "1i import sys; sys.path.insert(0, '$VENV_SITE')" ~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin/gimp3-rembg-plugin.py
```

This will prepend the venv’s package directory to `sys.path` so that GIMP’s Python interpreter can find `rembg`.

#### 4. Launch GIMP
```bash
gimp
```

> **⚠️ Expert-only fallback – not recommended**  
> If you absolutely cannot use a virtual environment and are fully aware of the risks, you can force‑install `rembg` into the system Python using `--break-system-packages`. This may break other system tools that rely on Python. **Use only in a dedicated virtual machine or test environment, and at your own risk.**
> ```bash
> python3 -m pip install --user "rembg[cpu]" --break-system-packages
> ```

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
- For Flatpak: ensure you installed rembg inside the Flatpak environment (Step 3 for Flatpak installation)
- For native with venv: verify that the `sed` command inserted the correct path. You can manually check the plugin file – the first line should be `import sys; sys.path.insert(0, '/home/your_user/.gimp3-rembg-venv/lib/python3.x/site-packages')`

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
