# AI Remove Background GIMP3 Plugin

This GIMP plugin allows users to remove image backgrounds using AI-powered tools like [rembg](https://github.com/danielgatis/rembg). The plugin integrates with GIMP3 to offer a simple way to remove backgrounds. It can process a single image in GIMP.

## Features

- **AI-Powered Background Removal:** Removes the background using the `rembg` tool, an AI-powered background removal library.

## Requirements

- **GIMP 2.99+**
- **Python 3.x** (For `rembg` to work)
- **rembg**: You need to have the `rembg` package installed in Python 3.x.


## Installation

1. **Clone or Download** this repository.
   ```bash
   git clone https://github.com/ismdevteam/gimp3-rembg-plugin.git
Install rembg in your Python 3 environment.

1.  **Install `rembg`** in your Python 3 environment.

     ```bash 
    flatpak run --command=bash org.gimp.GIMP --verbose
    python3 -m ensurepip --upgrade
    python3 -m pip install rembg[cli]

2.  **Copy the Plugin to GIMP**:

    -   Move the `gimp3-rembg-plugin` folder to your GIMP plugins folder:
        -   **Linux:** `~/.config/GIMP/2.99/plug-ins`
3.  **Restart GIMP** to load the plugin.
     ```bash
    flatpak run org.gimp.GIMP --verbose
    

Usage
-----

1.  **Open GIMP** and load an image.
2.  Go to **Filters > Developement > ISM Tools > AI Remove Background...**.
3.  Click it to run the plugin.

Example Workflow
----------------

1.  Open an image in GIMP that you want to remove the background from.
2.  Select **AI Remove Background** from the Filters > Developement > ISM Tools menu and click on it, or search for **plug-in-ai-remove-background** in Python-Fu menu.
3.  Run the plugin and watch as the background is removed and the image is processed.

Contributing
------------

Feel free to open issues or submit pull requests to improve this plugin! Contributions are always welcome.

License
-------

This project is licensed under the **GPLv3** License - see the <LICENSE> file for details.

Acknowledgments
---------------
-   **rembg**: This plugin integrates with [rembg](https://github.com/danielgatis/rembg) to handle AI-powered background removal.
-   **GIMP**: The GNU Image Manipulation Program, a free and open-source image editor.
