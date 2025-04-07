import bpy

"""
🧩 Common Blender Naming Suffixes
Suffix	Meaning	Example
OT_	Operator	MYADDON_OT_export_gltf
PT_	Panel	MYADDON_PT_export_ui
MT_	Menu	MYADDON_MT_custom_menu
HT_	Header	MYADDON_HT_view3d_header
UL_	UI List	MYADDON_UL_custom_ui_list
PR_	PropertyGroup (less common)	MYADDON_PR_export_settings

🍰 kimjafasu_ / KIMJAFASU_ as a unique prefix 
Basically a sigil from Kimja's Blender Fast To Unity
"""
from . import utils
from .blender2game import ExportSettings, ExportMessage, Blender2UnityPanel, ExportOperator, auto_export_gltf

modules = [
  utils
]

classes = (
    ExportMessage,
    ExportSettings,
    Blender2UnityPanel,
    ExportOperator,
)
    
def register():
    for mod in modules:
        mod.register()
        
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.gltf_export_settings = bpy.props.PointerProperty(type=ExportSettings)
    
    # Remove previous handlers to avoid duplicates
    bpy.app.handlers.save_post[:] = [h for h in bpy.app.handlers.save_post if h.__name__ != "auto_export_gltf"]
    
    # Add new handler
    bpy.app.handlers.save_post.append(auto_export_gltf)

def unregister():
    for mod in reversed(modules):
        mod.unregister()
        
    for cls in classes:
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.gltf_export_settings
    
    print([h.__name__ for h in bpy.app.handlers.save_post])
    if auto_export_gltf in bpy.app.handlers.save_post:
      bpy.app.handlers.save_post.remove(auto_export_gltf)


""" chatty explains
🧠 What does __name__ == "__main__" mean?

When a Python script is run directly (e.g. you press "Run Script" in Blender's Text Editor or run it via command line), 
Python sets a special built-in variable called __name__ to "__main__".

But when the same script is imported as a module into another script, __name__ will instead be set to the name of the 
file (like "blender2unity" or similar).

TLDR; "Only call register() if this script is being run directly, not if it's being imported by something else."
"""
if __name__ == "__main__":
    register()
