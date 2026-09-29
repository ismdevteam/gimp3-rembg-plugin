#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modified GIMP3 plugin to remove backgrounds from images
# Original author: James Huang <elastic192@gmail.com>
# Modified by: ismdevteam https://t.me/ismdevteam
# Inspired by: Tech Archive <medium.com/@techarchive>
# Date: 13/10/24

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gegl', '0.4')
from gi.repository import Gegl
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gio
from rembg import new_session, remove

import os, sys, string, tempfile, zipfile, shutil
import xml.etree.ElementTree as ET
import platform

def N_(message): return message
def _(message): return GLib.dgettext(None, message)

modelList = (
    "u2net",
    "u2net_human_seg",
    "u2net_cloth_seg",
    "u2netp",
    "silueta",
    "isnet-general-use",
    "isnet-anime",
    "sam"
)

class Goat (Gimp.PlugIn):
    ## GimpPlugIn virtual methods ##
    def do_query_procedures(self):
        return [ "plug-in-ai-remove-background" ]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(self, name,
                                            Gimp.PDBProcType.PLUGIN,
                                            self.run, None)

        procedure.set_image_types("*")
        procedure.set_sensitivity_mask (Gimp.ProcedureSensitivityMask.DRAWABLE)

        procedure.set_menu_label(_("AI Remove Background"))
        procedure.set_icon_name(GimpUi.ICON_GEGL)
        procedure.add_menu_path('<Image>/Filters/Development/ISM Tools AI Filters/')

        procedure.set_documentation(_("Removes the background using the `rembg` tool, an AI-powered background removal library."),
                                    _("Removes the background using the `rembg` tool, an AI-powered background removal library."),
                                    name)
        procedure.set_attribution("ismdevteam", "ismdevteam", "2024")

        # NOTE: No image return value is declared.
        # In batch mode (used by Batcher), returning a freshly loaded image
        # is not possible because such an image is not registered in GIMP's
        # image list.  Instead, the plugin replaces the layers of the image
        # it receives with the background-removed result.  Batcher's
        # "Edit Layers" mode relies on this in-place modification.

        return procedure

    # Helper: runs rembg on the merged image and returns the path to the
    # processed PNG.  The caller is responsible for cleaning up tempdir.
    def process_to_file(self, image, drawable, model_name, tempdir):
        rembg_session = new_session(model_name)

        def store_layer(image, drawable, tmp):
            interlace, compression = 0, 2

            width, height = drawable.get_width(), drawable.get_height()
            tmp_img = Gimp.Image.new(width, height, image.get_base_type())
            tmp_layer = Gimp.Layer.new_from_drawable (drawable, tmp_img)
            tmp_img.insert_layer (tmp_layer, None, 0)

            pdb_proc   = Gimp.get_pdb().lookup_procedure('file-png-export')
            pdb_config = pdb_proc.create_config()
            pdb_config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
            pdb_config.set_property('image', tmp_img)
            pdb_config.set_property('file', Gio.File.new_for_path(tmp))
            pdb_config.set_property('options', None)
            pdb_config.set_property('interlaced', interlace)
            pdb_config.set_property('compression', compression)
            pdb_config.set_property('bkgd', True)
            pdb_config.set_property('offs', False)
            pdb_config.set_property('phys', True)
            pdb_config.set_property('time', True)
            pdb_config.set_property('save-transparent', True)
            pdb_proc.run(pdb_config)
            tmp_img.delete()

        input_path  = os.path.join(tempdir, 'input.png')
        output_path = os.path.join(tempdir, 'output.png')

        thumb = image.duplicate()
        try:
            thumb_layer = thumb.merge_visible_layers (Gimp.MergeType.CLIP_TO_IMAGE)
            store_layer (thumb, thumb_layer, input_path)
        finally:
            # Clean up the duplicate so it does not leak as a stray image.
            thumb.delete()

        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input_data = i.read()
                output_data = remove(input_data, session=rembg_session)
                o.write(output_data)

        return output_path

    # In batch mode (Batcher), replace the layers of the original image
    # with the background-removed result.  No new image is created.
    def process_in_place(self, image, drawable, model_name):
        tempdir = tempfile.mkdtemp('gimp3-rembg-plugin')
        try:
            output_path = self.process_to_file(image, drawable, model_name, tempdir)

            procedure = Gimp.get_pdb().lookup_procedure('file-png-load')
            config = procedure.create_config()
            config.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
            config.set_property('file', Gio.File.new_for_path(output_path))
            result = procedure.run(config)
            loaded_image = result.index(1)

            layers = loaded_image.get_layers()
            source_layer = layers[0]

            # FIXED: remove all original layers so that the flattened result
            # consists only of the background-removed content.  Without this,
            # the transparent areas of the processed layer would reveal the
            # original background from the layer underneath.
            original_layers = list(image.get_layers())
            for layer in original_layers:
                image.remove_layer(layer)

            # Insert the processed layer into the (now empty) original image
            new_layer = Gimp.Layer.new_from_drawable(source_layer, image)
            image.insert_layer(new_layer, None, 0)

            loaded_image.delete()
        finally:
            # Always clean up the temp directory, even if something above failed.
            shutil.rmtree(tempdir, ignore_errors=True)

    # run() supports both interactive and non-interactive (batch) modes.
    def run(self, procedure, run_mode, image, drawables, config, run_data):
        if len(drawables) != 1:
            msg = _("Procedure '{}' only works with one drawable.").format(procedure.get_name())
            error = GLib.Error.new_literal(Gimp.PlugIn.error_quark(), msg, 0)
            return procedure.new_return_values(Gimp.PDBStatusType.CALLING_ERROR, error)
        else:
            drawable = drawables[0]

        if run_mode == Gimp.RunMode.INTERACTIVE:
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk
            gi.require_version('Gdk', '3.0')
            from gi.repository import Gdk

            GimpUi.init("gimp3-rembg-plugin")

            dialog = GimpUi.Dialog(use_header_bar=True,
            title=_("plug-in-ai-remove-background"),
            role="plugin-Python3")
            dialog.add_button(_("_Cancel"), Gtk.ResponseType.CANCEL)
            dialog.add_button(_("_OK"), Gtk.ResponseType.OK)

            builder = Gtk.Builder()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            builder.add_from_file(os.path.join(dir_path, "ui.glade"))

            box = builder.get_object("box")
            dialog.get_content_area().add(box)
            box.show()

            model_selector = builder.get_object("model_selector")

            while (True):
                response = dialog.run()
                if response == Gtk.ResponseType.OK:
                    model_name = model_selector.get_active_text()
                    dialog.destroy()

                    # Interactive: create a new image from the processed PNG
                    tempdir = tempfile.mkdtemp('gimp3-rembg-plugin')
                    try:
                        output_path = self.process_to_file(image, drawable, model_name, tempdir)

                        file=Gio.File.new_for_path(output_path)
                        procedure_load = Gimp.get_pdb().lookup_procedure('file-png-load')
                        config_load = procedure_load.create_config()
                        config_load.set_property('run-mode', Gimp.RunMode.NONINTERACTIVE)
                        config_load.set_property('file', file)
                        result = procedure_load.run(config_load)
                        new_image = result.index(1)
                    finally:
                        shutil.rmtree(tempdir, ignore_errors=True)

                    # Show the new image in a display
                    pdb_proc = Gimp.get_pdb().lookup_procedure('gimp-display-new')
                    pdb_config = pdb_proc.create_config()
                    pdb_config.set_property('image', new_image)
                    pdb_proc.run(pdb_config)

                    return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)
                else:
                    dialog.destroy()
                    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                                       GLib.Error())
        else:
            # Non-interactive (batch) mode: replace the image content in place.
            # Batcher will use the modified image for subsequent steps.
            model_name = "u2net"
            self.process_in_place(image, drawable, model_name)
            return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, None)


Gimp.main(Goat.__gtype__, sys.argv)
