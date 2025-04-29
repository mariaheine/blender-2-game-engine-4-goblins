import bpy
import os
from datetime import datetime

# ⚔️ Remember to import local modules like that!
from . import utils
from . import preprocess

"""
AI Disclaimer & Excuses

I'm mostly a C# programmer, so this plugin was made unter chatty's (ChatGPT) guide, 
it was a trial and error process, I learned a bunch about python and blender scripting, 
so it is an altogether fun ride and I am also happy with the results and can finally 
abandon ProBuilder for good.

Taking that into consideration this is by no means a professional battle-proven addon, 
might slowly grow into one, mostly a tool to rapidly prototype simple environments in 
blender to see changes almost instantly reflected unity in a possibly seamless way.

There are a bunch of code comments that explain to myself for future what some of 
the things do, I hope this is not too clumsy!
"""

class ExportOperator(bpy.types.Operator):
    """Export Selected Meshes to GLTF"""
    bl_idname = "export_scene.gltf_manual"
    bl_label = "Export GLTF"

    """
    This is the core of the operator. It contains the code that runs when the operator is invoked. 
    The return value should be {'FINISHED'} when the operation completes successfully. 
    If there is an error, you can return {'CANCELLED'}.
    """
    def execute(self, context):
        safe_export(context, "Manual Export")
        return {'FINISHED'}

def safe_export(context, message):
    settings = context.scene.gltf_export_settings
    settings.messages.clear() # Clear previous messages
    utils.kimjafasu_log_message(settings, message, "INFO")
    
    try:
        export_gltf(bpy.context, settings)
    except Exception as e:
        utils.kimjafasu_log_message(settings, f"Export failed: {e}.", 'ERROR')
        
    utils.kimjafasu_refresh_ui()

def auto_export_gltf(dummy):
    settings = bpy.context.scene.gltf_export_settings
    if settings.auto_export_on_save:
        safe_export(bpy.context, "Auto Export")
        
def export_gltf(context, settings):
    errors = utils.kimjafasu_get_export_errors(settings)
    
    if errors:
        for error in errors:
            utils.logging.kimjafasu_log_message(settings, error, 'WARNING')
        return
    
    # Filename
    if (settings.use_project_name):
        blend_filepath = bpy.data.filepath
        blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
        filename = blend_name
    else:
        filename = settings.simple_export_filename
    
    # Export location
    export_dir = bpy.path.abspath(settings.export_dir)

    # Making sure it exists
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)
        
    # 🪶 Neat oneliners    
    apply_modifiers = settings.apply_modifiers
    export_textures = settings.export_textures
    export_vertex_color = settings.export_vertex_color
    export_yup = False if settings.engine == 'Unreal' else True
    
    # 🪶 Export Path & Format
    gltf_export_format = settings.export_format
    
    if (settings.engine != "Procreate"):
        file_extension = {
            'GLB': ".glb",
            'GLTF_SEPARATE': ".gltf",
        }[gltf_export_format]
    else:
        file_extension = ".obj"
    
    export_path = os.path.join(export_dir, filename + file_extension)
    
    # 🪶 Save pre-export selection and mode
    # In order to later return to that state
    
    # Active object mode before exporting
    # https://docs.blender.org/api/current/bpy_types_enum_items/object_mode_items.html#rna-enum-object-mode-items
    """
    bpy.context.active_object: the last selected, 'active' object 
    bpy.context.selected_objects: all currently selected object
    
    bpy.context.active_object is equal to bpy.context.object (in most cases)
    
    using active_object is safer cos:
    
    "[...] during some modal operators or 
    when you're inside non-3D View editors, bpy.context.object might return 
    None, even though bpy.context.active_object still works."
    """
    selected_objects = [obj for obj in context.selected_objects] 
    active_object = bpy.context.active_object
    if active_object:
        original_mode = active_object.mode
    else: 
        # If no object is selected, default to Object Mode
        original_mode = 'OBJECT'
      
    # 🪶 Switch to Object mode if not already in it
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
        
    export_target = settings.export_target
    
    if export_target != 'Selection':
    
        bpy.ops.object.select_all(action='DESELECT')
        
        if export_target == 'Everything':
            for obj in bpy.data.objects:
                if obj.type in {'MESH', 'ARMATURE'}:
                    obj.select_set(True)
        elif export_target == 'Collection':
            export_collection = settings.export_collection
            for obj in export_collection.all_objects:
                if obj.type in {'MESH', 'ARMATURE'}:
                    obj.select_set(True)
    
    objects_to_be_exported = [obj for obj in context.selected_objects]
    split_objects, new_objects = preprocess.kimjafasu_preprocess_split_vertex_groups(bpy.context, objects_to_be_exported)
   
    # Combine original and split objects
    # Convert to sets, subtract, then combine
    # Now you can create the final export list:
    final_objects = [obj for obj in objects_to_be_exported if obj not in split_objects] + new_objects
    print("✨")
    bpy.ops.object.select_all(action='DESELECT')

    # Select all final objects
    for obj in final_objects:
        obj.select_set(True)

    # Set one of them (e.g., the first one) as active
    if final_objects:
        context.view_layer.objects.active = final_objects[0]

    # 🪶 Finally export.
    
    # A little override for procreate, everything else exported with gltf
    if (settings.engine == 'Procreate'):
        bpy.ops.wm.obj_export(
            filepath=export_path,
            check_existing=False,
            export_selected_objects=True,
            apply_modifiers=apply_modifiers,
            export_triangulated_mesh=True,
            export_object_groups=True,
            export_materials=True,
            forward_axis='NEGATIVE_Z',
            up_axis='Y'
        )
    else:
        # https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            # basics
            use_selection=True,
            export_yup=export_yup,
            export_apply=apply_modifiers,
            export_format=gltf_export_format,
            # animation
            export_skins=True,
            export_animations=True,
            # vertex color
            export_vertex_color=export_vertex_color,
            export_all_vertex_colors=True,
            export_active_vertex_color_when_no_material=True,
            # comptession
            # requires com.unity.draco
            # export_draco_mesh_compression_enable=True,
            # textures
            export_image_format='AUTO' if export_textures else 'NONE'
        )
        
    preprocess.kimjafasu_postprocess_cleanup(new_objects)
    
    # 🪶 Restore previous object selection
    if export_target != 'Selection':
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)
        
    # Restore original mode
    if original_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=original_mode)
    
    utils.kimjafasu_log_message(
      settings, 
      f"Successfuly exported {export_target} to {export_path}")