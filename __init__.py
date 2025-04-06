import bpy

"""
# Ensure we're pointing to the right directory for import
addon_directory = os.path.dirname(__file__)  # Gets the directory where __init__.py is located
sys.path.append(addon_directory)  # Adds that directory to the import path

if "blender2unity" in locals():
    importlib.reload(blender2unity)
else:
    importlib.import_module('blender2unity')
"""
from .blender2unity import ExportSettings, Blender2UnityPanel, ExportOperator, auto_export_gltf

classes = (
    ExportSettings,
    Blender2UnityPanel,
    ExportOperator,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.gltf_export_settings = bpy.props.PointerProperty(type=ExportSettings)
    
    # Remove previous handlers to avoid duplicates
    bpy.app.handlers.save_post[:] = [h for h in bpy.app.handlers.save_post if h.__name__ != "auto_export_gltf"]
    
    # Add new handler
    bpy.app.handlers.save_post.append(auto_export_gltf)

def unregister():
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
