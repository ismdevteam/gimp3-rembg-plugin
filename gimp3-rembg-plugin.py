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

import os, sys, string, tempfile, zipfile
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

        return procedure

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
                    dialog.destroy()
                    procedure = Gimp.get_pdb().lookup_procedure('gimp-message'); config = procedure.create_config(); config.set_property('message', 'init'); result = procedure.run(config); success = result.index(0)
                    
                    tempdir = tempfile.mkdtemp('gimp3-rembg-plugin')
                    
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
                        # write all PNG chunks except oFFs(ets)
                        pdb_config.set_property('bkgd', True)
                        pdb_config.set_property('offs', False)
                        pdb_config.set_property('phys', True)
                        pdb_config.set_property('time', True)
                        pdb_config.set_property('save-transparent', True)
                        pdb_proc.run(pdb_config)
                        tmp_img.delete()               
                    
                    input_path  = os.path.join(tempdir, 'input.png')
                    output_path = os.path.join(tempdir, 'output.png')
                    # save mergedimage
                    thumb = image.duplicate()
                    thumb_layer = thumb.merge_visible_layers (Gimp.MergeType.CLIP_TO_IMAGE)
                    store_layer (thumb, thumb_layer, input_path)

                    rembg_session = new_session(model_selector.get_active_text())
                    
                    with open(input_path, 'rb') as i:
                        with open(output_path, 'wb') as o:
                            input = i.read()
                            output = remove(input, session=rembg_session)
                            o.write(output)
                            

                    file=Gio.File.new_for_path(output_path)
                    procedure = Gimp.get_pdb().lookup_procedure('file-png-load'); config = procedure.create_config(); config.set_property('run-mode', Gimp.RunMode.INTERACTIVE); config.set_property('file', file); result = procedure.run(config); success = result.index(0); image = result.index(1)
                    procedure = Gimp.get_pdb().lookup_procedure('gimp-display-new'); config = procedure.create_config(); config.set_property('image', image); result = procedure.run(config); success = result.index(0); display = result.index(1)
              
                    os.remove(input_path)  
                    os.remove(output_path)
                    os.rmdir(tempdir)
                    
                    procedure = Gimp.get_pdb().lookup_procedure('gimp-message'); config = procedure.create_config(); config.set_property('message', 'done'); result = procedure.run(config); success = result.index(0)                   
                    break
                else:
                    dialog.destroy()
                    return procedure.new_return_values(Gimp.PDBStatusType.CANCEL,
                                                       GLib.Error())


Gimp.main(Goat.__gtype__, sys.argv)

