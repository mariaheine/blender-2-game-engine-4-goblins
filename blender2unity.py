import bpy
import os
from datetime import datetime

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
    
class ExportSettings(bpy.types.PropertyGroup):
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
            ('FBX', "FBX", "Exports as .fbx bleh proprietary file format")
        ],
        default='GLB',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    ) # type: ignore
    
    export_target : bpy.props.EnumProperty(
        name="Target",
        description="Choose which meshes to export",
        items=[
            ('Selection', "Selected only", "Exports only selected meshes."),
            ('Everything', "All of 'em", "Exports all meshes in the scene."),
            ('Collection', "Collection", "Exports meshes that are children of a target collection.")
        ],
        default='Selection'
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
    
    messages : bpy.props.CollectionProperty(type=ExportMessage) # type: ignore

class Blender2UnityPanel(bpy.types.Panel):
    bl_label = "Unity Exporter 🕊️"
    bl_idname = "VIEW3D_PT_unity_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '🕊️ Uni Exp'
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.gltf_export_settings
        
        layout.label(text="Hello there goblin/angel?")
        layout.separator() # BASIC SETTINGS
        
        layout.prop(settings, "export_dir", icon='EXPORT') # Export Directory Path
        layout.prop(settings, "export_format", icon='SHADERFX') # Dropdown for export format
        
        layout.separator() # WHAT TO EXPORT
        layout.label(text="Which meshes to export:")
        
        layout.prop(settings, "export_target", icon='SCENE_DATA')

        if settings.export_target == 'Collection':
            layout.prop(settings, "export_collection", icon='OUTLINER_COLLECTION')
        
        layout.separator() # TWEAKS
        
        layout.label(text="Tweaks:")        
        layout.prop(settings, "auto_export_on_save", icon='RNA') # Toggle Auto Export
        
        layout.separator() # GLTF SETTINGS
        
        if scene.gltf_export_settings.export_format != 'FBX':
            layout.label(text="GLTF/GLB Settings:")
            layout.prop(settings, "export_textures", icon="TEXTURE") # Export Textures
            layout.prop(settings, "apply_modifiers", icon='MODIFIER') # Apply Modifiers
            layout.separator()
        
        errors = get_export_errors(settings)

        if errors:
            for msg in errors:
                layout.label(text=msg, icon='ERROR')
        else:
            layout.operator("export_scene.gltf_manual", text="Export!", icon='GHOST_ENABLED')
        
        layout.separator()
        
        if settings.messages:
            box = layout.box()
            box.label(text="Latest export status:")
            
            for msg in settings.messages:
                icon = {
                    'INFO': 'INFO',
                    'WARNING': 'ERROR',  # Blender doesn't have a WARNING icon
                    'ERROR': 'CANCEL',
                    'NEWLINE': 'ADD'
                }.get(msg.level, 'INFO')
                box.label(text=msg.text, icon=icon)

# gosh multilines, why so hard, try this onetime: https://b3d.interplanety.org/en/multiline-text-in-blender-interface-panels/
def log_message(self, text, level='INFO'):
    now = datetime.now().strftime("%H:%M:%S")
    text = f"[{now}] {text}"
    
    console_print(text, level)
    
    lines = []
    if(len(text)) > 50:
        lines = split_message(text, 50)
    else:
        lines.append(text)
    
    for index, line in enumerate(lines):
        msg = self.messages.add()
        msg.text = line
        if index != 0:
            level = 'NEWLINE'
        msg.level = level
    
def console_print(text, level):
    if level == 'INFO':
      prefix = f"🕊️  [INFO @{__name__}]"
    elif level == 'WARNING':
      prefix = f"⚔️  [WARNING @{__name__}"
    elif level == 'ERROR':
      prefix = f"🔥 [ERROR @{__name__}]"
    else:
      prefix = ""
    print(f"{prefix} {text}")
    
def split_message(message, max_length=50):
    lines = []
    while len(message) > max_length:
        split_point = message.rfind(" ", 0, max_length)
        if split_point == -1:
            split_point = max_length
        lines.append(message[:split_point])
        message = message[split_point:].lstrip()
    lines.append(message)
    return lines
            
def get_export_errors(settings):
    errors = []
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        errors.append("Save your .blend file first!")
    if not settings.export_dir:
        errors.append("Can't export, need valid Export Dir.")
    if settings.export_target == 'Collection' and not settings.export_collection:
        errors.append("Export target is 'Collection', but no collection is selected.")
    return errors
  
def refresh_ui():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':  # or 'PROPERTIES', etc.
                area.tag_redraw()
  
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
        safe_export(context)
        return {'FINISHED'}

def safe_export(context):
    settings = context.scene.gltf_export_settings
    settings.messages.clear() # Clear previous messages
    
    try:
        export_gltf(bpy.context, settings)
    except Exception as e:
        log_message(settings, f"Export failed: {e}.", 'ERROR')
        
    refresh_ui()

def auto_export_gltf(dummy):
    settings = bpy.context.scene.gltf_export_settings
    if settings.auto_export_on_save:
        safe_export(bpy.context)
        
# Function to export GLTF
def export_gltf(context, settings):
    
    errors = get_export_errors(settings)
    
    if errors:
        for error in errors:
            msg = settings.messages.add()
            msg.text = error
            msg.level = 'WARNING'
    
    blend_filepath = bpy.data.filepath
    blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
    export_dir = bpy.path.abspath(settings.export_dir)

    # Ensure export directory exists
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Read the apply transforms setting from the UI
    apply_modifiers = settings.apply_modifiers
    export_textures = settings.export_textures 
    
    # Export Path & Format
    export_format = settings.export_format
    
    file_extension = {
        'GLB': ".glb",
        'GLTF_SEPARATE': ".gltf",
        'FBX': ".fbx"
    }[export_format]
    
    export_path = os.path.join(export_dir, blend_name + file_extension)
    
    export_target = settings.export_target
    
    if export_target != 'Selection':
    
        selected_objects = [obj for obj in bpy.context.selected_objects] # Save current selection
        bpy.ops.object.select_all(action='DESELECT')
        
        if export_target == 'Everything':
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    obj.select_set(True)
        elif export_target == 'Collection':
            export_collection = settings.export_collection
            for obj in export_collection.all_objects:
                if obj.type == 'MESH':
                    obj.select_set(True)
    
   
    # Export logic for each format
    if export_format in {'GLB', 'GLTF_SEPARATE'}:
        # https://docs.blender.org/api/current/bpy.ops.export_scene.html#bpy.ops.export_scene.gltf
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            export_format=export_format,
            use_selection=True,
            export_apply=apply_modifiers,
            export_yup=True,
            export_image_format='AUTO' if export_textures else 'NONE'
        )
    elif export_format == 'FBX':
        bpy.ops.export_scene.fbx(
            filepath=export_path,
            use_selection=True,
            apply_unit_scale=True,
            apply_scale_options='FBX_SCALE_UNITS',
            bake_space_transform=True if apply_transforms else False,
            axis_forward='-Z',
            axis_up='Y'
        )
        
    
    # If export is successful
    # settings.export_status = f"✅ Exported successfully to {export_path}"
    
    if export_target != 'Selection':
        # Restore previous selection
        # When export target == 'Selection' there is no need to revert back to it, it was not overwritten.
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)

    print(f"✅ GLTF Exported to: {export_path}")
    

        
        
