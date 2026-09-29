# AI Remove Background GIMP3 Plugin

This GIMP plugin allows users to remove image backgrounds using AI-powered tools like [rembg](https://github.com/danielgatis/rembg). The plugin integrates with GIMP3 to offer a simple way to remove backgrounds. It can process a single image in GIMP, either interactively or as part of an automated batch workflow (e.g. with the Batcher plugin or a Python-Fu script).

## Features

- **AI-Powered Background Removal:** Removes the background using the `rembg` tool, an AI-powered background removal library.
- **Multiple AI Models:** Choose from various models like u2net, isnet-general-use, sam, and more.
- **Simple Integration:** Works seamlessly within GIMP's interface.
- **Batch / Batcher Compatible:** In non-interactive mode the plugin replaces the image content in place, making it usable from GIMP's batch interpreter (`--batch-interpreter=python-fu-eval`) and from automation plugins such as Batcher.

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

### Interactive (GIMP UI)

1. **Open GIMP** and load an image.
2. Go to **Filters → Development → ISM Tools AI Filters → AI Remove Background...**
3. Configure the options:
   - **Model:** Choose which AI model to use for background removal (default: u2net).
4. Click **OK** to run the plugin.
5. A new image window opens containing the subject on a transparent background.

### Batch (Python-Fu)

The plugin can be invoked non-interactively via GIMP's Python-Fu batch interpreter. In this mode it **replaces the layers of the image in place** with the background-removed result. This is the same behaviour required by automation plugins such as Batcher.

The following script loads an image, removes its background, and saves the result with transparency preserved:

```bash
flatpak run org.gimp.GIMP -i --batch-interpreter=python-fu-eval -b '
import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, Gio

pdb = Gimp.get_pdb()

# Load the input image
proc = pdb.lookup_procedure("gimp-file-load")
cfg = proc.create_config()
cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
cfg.set_property("file", Gio.File.new_for_path("/path/to/input.png"))
image = proc.run(cfg).index(1)

# Run the plugin
drawables = image.get_selected_drawables()
proc = pdb.lookup_procedure("plug-in-ai-remove-background")
cfg = proc.create_config()
cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
cfg.set_property("image", image)
cfg.set_core_object_array("drawables", drawables)
proc.run(cfg)

# Export the result.  NOTE: do NOT call image.flatten() before exporting —
# the plugin already produced a single layer with an alpha channel, and
# flatten() would composite it onto the background colour and lose
# transparency.
proc = pdb.lookup_procedure("file-png-export")
cfg = proc.create_config()
cfg.set_property("run-mode", Gimp.RunMode.NONINTERACTIVE)
cfg.set_property("image", image)
cfg.set_property("file", Gio.File.new_for_path("/path/to/output.png"))
proc.run(cfg)

# Quit
proc = pdb.lookup_procedure("gimp-quit")
cfg = proc.create_config()
proc.run(cfg)
'
```

**Important:** do **not** call `image.flatten()` after the plugin in batch mode. Use `image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)` if you need to collapse layers while preserving alpha, or simply export the image directly.

### Batch (Batcher plugin)

To use this plugin with [Batcher](https://github.com/kamilburda/gimp-batcher):

1. Open GIMP interactively.
2. Add an **AI Remove Background** step to your Batcher workflow.
3. Make sure the step **after** the AI step does not force a flatten (which would composite the transparent pixels onto a solid background). Prefer "Merge visible layers" or export directly.
4. Run the workflow.

Because the plugin replaces the layers in place and returns success without declaring an image return value, Batcher can continue the workflow without any `NULL` errors.

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

When run in batch mode, the plugin always uses the default model (`u2net`). To use a different model in batch mode, either invoke the plugin via Python-Fu with the model set on its config, or use Batcher's model-selection field if it supports one.

## Troubleshooting

### Plugin doesn't appear in menu
- Verify the plugin is in `~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin/`
  - **For Flatpak GIMP:** the plugin directory is `~/.var/app/org.gimp.GIMP/config/GIMP/3.0/plug-ins/`
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

### Batch command fails with "PDB procedure returned NULL GIMP object"
- This is an old error from before the plugin supported batch mode. Update to the current version, which handles `RUN-NONINTERACTIVE` and does not return an image.

### Batch command fails with "does not have property 'run-mode'"
- Some procedures (e.g. `gimp-quit`) do not expose a `run-mode` property. Simply omit that line from your script.

### Batch command produces a white background instead of transparency
- Remove any `image.flatten()` call before exporting. `flatten()` composites the layer onto the current background colour and discards alpha. Export the image directly, or use `image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)` instead.

### Batcher fails with "Trying to add item ... to wrong image"
- This error occurred in an earlier version of the plugin that used `Layer.copy()`. Update to the current version, which uses `Gimp.Layer.new_from_drawable(source_layer, image)`.

## Contributing

Feel free to open issues or submit pull requests to improve this plugin! Contributions are always welcome.

## License

This project is licensed under the **GPLv3** License - see the LICENSE file for details.

## Acknowledgments

- **rembg**: This plugin integrates with [rembg](https://github.com/danielgatis/rembg) to handle AI-powered background removal.
- **GIMP**: The GNU Image Manipulation Program, a free and open-source image editor.
- **All AI model contributors**: For making their models available for public use.
