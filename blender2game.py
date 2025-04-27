import bpy
import os
from datetime import datetime

# ⚔️ Remember to import local modules like that!
from . import utils

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

class ExportMessage(bpy.types.PropertyGroup):
    text: bpy.props.StringProperty(name="Message") # type: ignore
    level: bpy.props.EnumProperty(
        name="Level",
        items=[
            ('INFO', "Info", ""),
            ('WARNING', "Warning", ""),
            ('ERROR', "Error", ""),
            ('NEWLINE', "New Line", "")
        ], 
        default='INFO'
    ) # type: ignore
    
class SectionToggles(bpy.types.PropertyGroup):
    basics_foldout: bpy.props.BoolProperty(name="Basics first", default=True)  # type: ignore
    what_export_foldout: bpy.props.BoolProperty(name="What to export", default=False)  # type: ignore
    gltf_settings_foldout: bpy.props.BoolProperty(name="GLTF/GLB settings", default=False)  # type: ignore
    show_logs_foldout: bpy.props.BoolProperty(name="Logs", default=False)  # type: ignore
    
class ExportSettings(bpy.types.PropertyGroup):
    messages : bpy.props.CollectionProperty(type=ExportMessage) # type: ignore
    
    selection_toggles : bpy.props.PointerProperty(
        name="Selection Toggles",
        type=SectionToggles
    ) # type: ignore
    
    export_dir : bpy.props.StringProperty(
        name="Export Dir",
        description="🕊️ Directory where the GLTF file will be saved",
        default="",
        subtype='DIR_PATH',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    ) # type: ignore
    
    apply_modifiers : bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers (excluding Armatures) to mesh objects; WARNING: prevents exporting shape keys.",
        default=False
    ) # type: ignore
    
    export_vertex_color : bpy.props.EnumProperty(
        name="Vert Col",
        description="If and how to export vertex color.",
        items=[
            ('MATERIAL', "Material", "Export vertex color when used by material."),
            ('ACTIVE', "All", "Export all mesh vertex color data. Even when no material is set."),
            ('NONE', "None", "Do not export vertex color."),
        ],
        default='ACTIVE',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    ) # type: ignore
    
    export_textures : bpy.props.BoolProperty(
        name="Export Textures",
        description="Include textures in the export. Works only for gltf & glb.",
        default=False
    ) # type: ignore
    
    export_format : bpy.props.EnumProperty(
        name="Format",
        description="Choose export format",
        items=[
            ('GLB', "GLB (Recommended)", "Exports a single .glb file"),
            ('GLTF_SEPARATE', "GLTF + BIN", "Exports separate .gltf and .bin files"),
        ],
        default='GLB',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    ) # type: ignore
    
    engine : bpy.props.EnumProperty(
        name="Engine",
        description="Choose your target Game Engine",
        items=[
            ('Unity', "Unity (Y-Up)", ""),
            ('Godot', "Godot (Y-up)", ""),
            ('Unreal', "Unreal (Z-up)", ""),
            ('Procreate', "Procreate (Y-up)", "Not really a game engine I know, but if u like to paint models there like me, then this tool might also be useful, it overrdes export format to .obj since that is the only .")
        ],
        default='Unity',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    ) # type: ignore
    
    use_simple_mode : bpy.props.BoolProperty(
      name="Simple Export Selection",
      description="Choose between a simple export selection, where all objects selected for export will be put into one file or an ability to set specialized export groups.",
      default=True
    ) # type: ignore
    
    use_project_name : bpy.props.BoolProperty(
      name="Use .blend project filename",
      description="Will use the same filename for the exported object as the current .blend project name.",
      default=True
    ) # type: ignore
    
    simple_export_filename : bpy.props.StringProperty(
        name="Filename",
        description="Filename for the exported model",
        default="",
        subtype='FILE_NAME',
    ) # type: ignore
    
    export_target : bpy.props.EnumProperty(
        name="Target",
        description="Choose which meshes to export",
        items=[
            ('Selection', "Selected only", "Exports only selected meshes."),
            ('Everything', "All meshes in the scene", "Exports all meshes in the scene."),
            ('Collection', "Collection", "Exports only the meshes that are children of a target collection.")
        ],
        default='Everything'
    ) # type: ignore
    
    export_collection : bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection,
        description="All children meshes of this collection will be exported."
    ) # type: ignore

    auto_export_on_save : bpy.props.BoolProperty(
        name="Auto-Export on Save",
        description="Automatically export when saving the .blend file",
        default=False
    ) # type: ignore
    

# Icons ref: https://blenderartists.org/t/icon-reference-sheets-2-79-2-80/1162781
class Blender2UnityPanel(bpy.types.Panel):
    bl_label = "Universal Game Exporter 🕊️"
    bl_idname = "VIEW3D_PT_unity_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '🕊️ Uni Exp'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.gltf_export_settings
        toggles = settings.selection_toggles
        
        layout.label(text="Hello there goblin/angel!")
        layout.separator() # BASIC SETTINGS
        
        layout.prop(toggles, "basics_foldout", icon="TRIA_DOWN" if toggles.basics_foldout else "TRIA_RIGHT", emboss=False)
        if toggles.basics_foldout:
            layout.prop(settings, "export_dir", icon='EXPORT') # Export Directory Path
            
            layout.prop(settings, "export_format", icon='SHADERFX') # Dropdown for export format
            layout.prop(settings, "engine", icon='SYSTEM')
        
        layout.separator() # WHAT TO EXPORT
        
        layout.prop(toggles, "what_export_foldout", icon="TRIA_DOWN" if toggles.what_export_foldout else "TRIA_RIGHT", emboss=False)
        if toggles.what_export_foldout:
            box = layout.box()
            box.prop(settings, "use_simple_mode", icon='MESH_MONKEY')
            if (settings.use_simple_mode):
                box.prop(settings, "use_project_name")
                if (settings.use_project_name == False):
                    box.prop(settings, "simple_export_filename", icon='COPY_ID')
                box.label(text="What gets exported:", icon='SCENE_DATA')
                box.prop(settings, "export_target")

                if settings.export_target == 'Collection':
                    box.prop(settings, "export_collection", icon='OUTLINER_COLLECTION')
            else:                
                box.label(text="Not yet implemented")
            
        layout.separator() # GLTF SETTINGS
        
        layout.prop(toggles, "gltf_settings_foldout", icon="TRIA_DOWN" if toggles.gltf_settings_foldout else "TRIA_RIGHT", emboss=False)
        if toggles.gltf_settings_foldout:
            box = layout.box()
            box.prop(settings, "export_textures", icon="TEXTURE") # Export Textures
            box.prop(settings, "apply_modifiers", icon='MODIFIER') # Apply Modifiers
            box.prop(settings, "export_vertex_color", icon='VPAINT_HLT') # Dropdown for export format
        layout.separator()
        
        layout.prop(toggles, "show_logs_foldout", icon="TRIA_DOWN" if toggles.show_logs_foldout else "TRIA_RIGHT", emboss=False)
        if toggles.show_logs_foldout:
            if settings.messages:
                box = layout.box()
                box.label(text="Latest export status:")
                
                for msg in settings.messages:
                    icon = {
                        'INFO': 'INFO',
                        'WARNING': 'ERROR',  # Blender doesn't have a WARNING icon
                        'ERROR': 'CANCEL',
                        'NEWLINE': 'BLANK1'
                    }.get(msg.level, 'INFO')
                    box.label(text=msg.text, icon=icon)
        
        layout.separator()
              
        layout.prop(settings, "auto_export_on_save", icon='RNA') # Toggle Auto Export
        
        errors = get_export_errors(settings)

        if errors:
            for msg in errors:
                layout.label(text=msg, icon='ERROR')
        else:
            if (settings.auto_export_on_save == False):
                layout.operator("export_scene.gltf_manual", text="Manual Export", icon='GHOST_ENABLED')
        
            
def get_export_errors(settings):
    errors = []
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        errors.append("Save your .blend file first!")
    if not settings.export_dir:
        errors.append("Can't export, need valid Export Dir.")
    if not settings.use_project_name and not settings.simple_export_filename:
        errors.append("Please set an export filename.")
    if settings.export_target == 'Selection':
        has_any_mesh_selected = any(obj.type =='MESH' for obj in bpy.context.selected_objects)
        if not has_any_mesh_selected:
            errors.append("Export target is 'Selection', but not a single mesh is selected.")
    if settings.export_target == 'Collection' and not settings.export_collection:
        errors.append("Export target is 'Collection', but no collection is selected.")
    return errors
  
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
    errors = get_export_errors(settings)
    
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

    # Read the apply transforms setting from the UI
    apply_modifiers = settings.apply_modifiers
    export_textures = settings.export_textures
    export_vertex_color = settings.export_vertex_color
    
    # Export Path & Format
    gltf_export_format = settings.export_format
    
    if (settings.engine != "Procreate"):
        file_extension = {
            'GLB': ".glb",
            'GLTF_SEPARATE': ".gltf",
        }[gltf_export_format]
    else:
        file_extension = ".obj"
    
    export_path = os.path.join(export_dir, filename + file_extension)
    
    # Save currently selected objects
    selected_objects = [obj for obj in context.selected_objects] 
    
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
    active_object = bpy.context.active_object
    if active_object:
        original_mode = active_object.mode
    else: 
        # If no object is selected, default to Object Mode
        original_mode = 'OBJECT'
      
    # Switch to Object mode if not already in it
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
   
    export_yup = False if settings.engine == 'Unreal' else True

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

    
    # Restore previous object selection
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