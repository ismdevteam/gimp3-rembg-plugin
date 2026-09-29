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

On Debian 13 (trixie) with GIMP 3.0.4 from APT, the tested working approach uses a Python **virtual environment** that supplies both the plugin's GIMP bindings (`pygobject`) and `rembg`. **GIMP must be launched from within the activated venv** so its Python subprocess inherits the venv's `sys.path`.

> ⚠️ **Download the plugin first.** The `requirements.txt` file lives inside the plugin folder, so it must exist before you run `pip install -r requirements.txt`.

#### 1. Install GIMP and Python tools
```bash
sudo apt install gimp python3-pip python3-venv
```

#### 2. Download the plugin
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

# Verify files (you should see gimp3-rembg-plugin.py, ui.glade, README.md, requirements.txt)
ls -la gimp3-rembg-plugin/
```

#### 3. Create the venv and install dependencies
```bash
# Create a dedicated venv
python3 -m venv ~/.gimp3-rembg-venv

# Activate it
source ~/.gimp3-rembg-venv/bin/activate

# Install from the manifest shipped with the plugin
cd ~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin/
pip install -r requirements.txt

# (Optional, GPU only) Replace CPU onnxruntime with the GPU build:
# pip uninstall -y onnxruntime
# pip install onnxruntime-gpu

deactivate
```

The manifest installs three things:

- `pygobject` — the GObject bindings the plugin uses (`import gi`)
- `rembg[cli,cpu]` — the AI background-removal library and its CPU inference backend
- `onnxruntime` — the inference runtime (already pulled in by `rembg[cpu]`, listed explicitly for clarity)

#### 4. Launch GIMP from the activated venv

```bash
source ~/.gimp3-rembg-venv/bin/activate
gimp
```

When GIMP is started from the activated venv, its Python subprocess inherits the venv's `sys.path`, so `import gi` and `import rembg` both resolve to the venv. The plugin then loads without further configuration.

To avoid typing the activation command every time, add an alias to `~/.bashrc`:

```bash
alias gimp-rembg='source ~/.gimp3-rembg-venv/bin/activate && gimp'
```

Then run `gimp-rembg` instead of `gimp` whenever you want to use the plugin.

> **⚠️ Expert-only fallback – not recommended**  
> If you absolutely cannot use a venv and are fully aware of the risks, you can install just the runtime library into the user site:
> ```bash
> pip install --user --break-system-packages "rembg[cpu]"
> ```
> **Do not install `pygobject` this way.** `--break-system-packages` combined with `pygobject` can overwrite or shadow the system `pygobject` that many GTK applications depend on. **Never** run `pip install --user --break-system-packages -r requirements.txt` from this repository — the manifest is intended for a venv only. The runtime library alone is enough because the system Python already provides `gi`.

## Using requirements.txt

The repository ships a `requirements.txt`:

```
pygobject
rembg[cli,cpu]
onnxruntime
```

Install it from inside the venv, **after** downloading the plugin:

```bash
cd ~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin
source ~/.gimp3-rembg-venv/bin/activate
pip install -r requirements.txt
deactivate
```

**Why these three?**

- `pygobject` is required so the plugin's `import gi` succeeds when GIMP is launched from a venv.
- `rembg[cli,cpu]` provides the `rembg` Python API and CPU inference. The `cli` extra is technically not used by the plugin, but it makes the venv self-contained and mirrors a known-good configuration. If you prefer a leaner install, replace this line with `rembg[cpu]`.
- `onnxruntime` is already pulled in by `rembg[cpu]`; listing it explicitly is optional but harmless.

**Do not add `onnxruntime-gpu` to this file.** It conflicts with `onnxruntime` and is a ~250 MB download that only helps if you have a CUDA-capable GPU. Install it manually as shown in Step 3.

**Do not use this file with `--break-system-packages`.** The `pygobject` line is safe inside a venv but dangerous against the system Python. For the expert fallback, install `rembg[cpu]` directly and skip the manifest.

**Flatpak users:** the manifest is not used. Flatpak GIMP has its own Python environment; follow the `python3 -m pip install "rembg[cpu]"` instructions inside `flatpak run --command=bash org.gimp.GIMP` instead.

## Usage

### Interactive (GIMP UI)

1. **Open GIMP** (with the venv activated, or via the alias described above) and load an image.
2. Go to **Filters → Development → ISM Tools AI Filters → AI Remove Background...**
3. Configure the options:
   - **Model:** Choose which AI model to use for background removal (default: u2net).
4. Click **OK** to run the plugin.
5. A new image window opens containing the subject on a transparent background.

### Batch (Python-Fu)

The plugin can be invoked non-interactively via GIMP's Python-Fu batch interpreter. In this mode it **replaces the layers of the image in place** with the background-removed result. This is the same behaviour required by automation plugins such as Batcher.

The following script loads an image, removes its background, and saves the result with transparency preserved:

```bash
gimp -i --batch-interpreter=python-fu-eval -b '
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

For Flatpak GIMP, prefix the command with `flatpak run org.gimp.GIMP`.  
For native GIMP with a venv, use `source ~/.gimp3-rembg-venv/bin/activate && gimp` or use the `gimp-rembg` alias.

**Important:** do **not** call `image.flatten()` after the plugin in batch mode. Use `image.merge_visible_layers(Gimp.MergeType.CLIP_TO_IMAGE)` if you need to collapse layers while preserving alpha, or simply export the image directly.

### Batch (Batcher plugin)

To use this plugin with [Batcher](https://github.com/kamilburda/gimp-batcher):

1. Open GIMP from the activated venv (or via the `gimp-rembg` alias).
2. Add an **AI Remove Background** step to your Batcher workflow.
3. Make sure the step **after** the AI step does not force a flatten (which would composite the transparent pixels onto a solid background). Prefer "Merge visible layers" or export directly.
4. Run the workflow.

Because the plugin replaces the layers in place and returns success without declaring an image return value, Batcher can continue the workflow without any `NULL` errors.

## First Run Notes

On the first run with a new model:
- The AI model files are downloaded automatically (~176 MB for `u2net`)
- This may take a few minutes depending on your internet connection
- Files are saved to rembg's cache directory. On rembg 2.0.85 the path is:
  - Native: `~/.rembg/models/<model_name>/<model_name>.onnx`
  - Flatpak: `~/.var/app/org.gimp.GIMP/data/.rembg/models/...` (or the equivalent inside the sandbox)
- Subsequent runs are much faster as the model is cached locally

Example download progress (rembg 2.0.85 on native Debian):
```
Downloading data from 'https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx' to file '/home/user/.rembg/models/u2net/u2net.onnx'.
100%|████████████████████████████████████████| 176M/176M [00:15<00:00, 956GB/s]
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

### `ModuleNotFoundError: No module named 'rembg'`
- **venv (native install):** GIMP was not launched from the activated venv. Activate the venv first (`source ~/.gimp3-rembg-venv/bin/activate`) and then run `gimp`. Or use the `gimp-rembg` alias described in Step 4.
- **Flatpak:** ensure you installed rembg inside the Flatpak environment.

### `ModuleNotFoundError: No module named 'gi'`
- GIMP was launched from the system shell, not from the activated venv, so the plugin's `import gi` could not find the venv's `pygobject`.
- Activate the venv (`source ~/.gimp3-rembg-venv/bin/activate`) and run `gimp` from there.
- Verify the venv has `pygobject` installed: `source ~/.gimp3-rembg-venv/bin/activate && pip list | grep -i pygobject`.

### `Failed to execute child process ... (Exec format error)`
- A non-shebang line ended up **before** `#!/usr/bin/env python3`. Restore the shebang as the first line.

### `pip install -r requirements.txt` says "No such file or directory"
- Make sure you unzipped the plugin into `~/.config/GIMP/3.0/plug-ins/gimp3-rembg-plugin/` and are running `pip install` from inside that directory.

### dependency conflicts with other user-installed packages
- The venv approach isolates the plugin from your other Python packages, so this problem should not arise.
- If you used the expert-only fallback with `--break-system-packages`, you may see conflicts (for example `electrum` complaining about `protobuf`). Prefer the venv. **Never** install `pygobject` with `--break-system-packages`.

### First model download fails
- Ensure network connectivity
- Check disk space in your home directory

### Processing is slow
- The CPU backend is slower. If you have a compatible NVIDIA GPU, install `onnxruntime-gpu` into the venv (see Step 3) and remove `onnxruntime`.
- Larger images take more time. Consider resizing very large images first.

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
