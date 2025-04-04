import bpy
import os

# icon references https://blenderartists.org/t/icon-reference-sheets-2-79-2-80/1162781

class GLTFExportSettings(bpy.types.PropertyGroup):
    export_dir: bpy.props.StringProperty(
        name="Export Dir",
        description="🕊️ Directory where the GLTF file will be saved",
        default="",
        subtype='DIR_PATH',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    )
    
    apply_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers (excluding Armatures) to mesh objects; WARNING: prevents exporting shape keys.",
        default=False
    )
    
    export_textures: bpy.props.BoolProperty(
        name="Export Textures",
        description="Include textures in the export. Works only for gltf & glb.",
        default=False  # Textures are included by default
    )
    
    export_format: bpy.props.EnumProperty(
        name="Format",
        description="Choose export format",
        items=[
            ('GLB', "GLB (Recommended)", "Exports a single .glb file"),
            ('GLTF_SEPARATE', "GLTF + BIN", "Exports separate .gltf and .bin files"),
            ('FBX', "FBX", "Exports as .fbx bleh proprietary file format")
        ],
        default='GLB'
    )

    auto_export_on_save: bpy.props.BoolProperty(
        name="Auto-Export on Save",
        description="Automatically export when saving the .blend file",
        default=False
    )
    
    export_status: bpy.props.StringProperty(
        name="Export Status",
        description="Displays the result of the export process",
        default=""  # Default empty, you will set this dynamically
    )

class Blender2UnityPanel(bpy.types.Panel):
    bl_label = "Unity Exporter 🕊️"
    bl_idname = "VIEW3D_PT_unity_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '🕊️ Uni Exp'  # The name of the tab where the panel will appear
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        row = layout.row()
        
        layout.label(text="Hello there goblin/angel (choose your class)")
        
        layout.separator()  # Adds some spacing
        
        # Export Directory Path
        layout.prop(scene.gltf_export_settings, "export_dir", icon='EXPORT')
        
        # Dropdown for export format
        layout.prop(scene.gltf_export_settings, "export_format", icon='SHADERFX') 
        
        layout.separator() 
        layout.label(text="Tweaks:")
        
        
        # Toggle Auto Export
        layout.prop(scene.gltf_export_settings, "auto_export_on_save", icon='RNA')  
        
        #layout.row().label(text="---------" * 10, icon="INFO")
        layout.separator()
        
        if scene.gltf_export_settings.export_format != 'FBX':
            layout.label(text="GLTF/GLB Settings:")
            # Export Textures
            layout.prop(scene.gltf_export_settings, "export_textures", icon="TEXTURE")
            
            # Apply Transforms Checkbox
            layout.prop(scene.gltf_export_settings, "apply_modifiers", icon='MODIFIER')
            layout.separator()
        
        # Check if the export dir is empty and display a warning message
        if not scene.gltf_export_settings.export_dir:
            # Disable the export button
            layout.label(text="Can't export, need valid Export Dir.", icon='GHOST_DISABLED')
        else:                
            # Export Button
            row = layout.row()
            row.operator("export_scene.gltf_manual", text="Export!", icon='GHOST_ENABLED')
        
        #layout.separator()  # Adds spacing before the status box
        # Display a message in a box
        #if scene.gltf_export_settings.export_status:
        #    # Add a box and display the message
        #    box = layout.box()
        #    box.label(text=scene.gltf_export_settings.export_status)
        #else:
        #    # If no status, display a placeholder
        #    box = layout.box()
        #    box.label(text="No export attempt made yet.")


class ExportGLTFOperator(bpy.types.Operator):
    """Export Selected Meshes to GLTF"""
    bl_idname = "export_scene.gltf_manual"
    bl_label = "Export GLTF"

    # This is the core of the operator. It contains the code that runs when the operator is invoked. 
    # The return value should be {'FINISHED'} when the operation completes successfully. 
    # If there is an error, you can return {'CANCELLED'}.
    def execute(self, context):
        export_gltf(context)
        return {'FINISHED'}
    
# Function to export GLTF
def export_gltf(context):
    if not context.scene.gltf_export_settings.export_dir:
        print("blender2unity errer: Export directory is not set! Skipping export.")
        return
    
    blend_filepath = bpy.data.filepath
    if not blend_filepath:
        print("❌ Save your .blend file first!")
        return
    
    blend_name = os.path.splitext(os.path.basename(blend_filepath))[0]
    export_dir = bpy.path.abspath(context.scene.gltf_export_settings.export_dir)

    # Ensure export directory exists
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Read the apply transforms setting from the UI
    apply_modifiers = context.scene.gltf_export_settings.apply_modifiers
    export_textures = context.scene.gltf_export_settings.export_textures 
    
    # Export Path & Format
    export_format = context.scene.gltf_export_settings.export_format
    
    file_extension = {
        'GLB': ".glb",
        'GLTF_SEPARATE': ".gltf",
        'FBX': ".fbx"
    }[export_format]
    
    export_path = os.path.join(export_dir, blend_name + file_extension)
    
    
    # Save current selection
    selected_objects = [obj for obj in bpy.context.selected_objects]

    # Select only mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
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
    context.scene.gltf_export_settings.export_status = f"✅ Exported successfully to {export_path}"
        
    # Restore previous selection
    bpy.ops.object.select_all(action='DESELECT')
    for obj in selected_objects:
        obj.select_set(True)

    print(f"✅ GLTF Exported to: {export_path}")
    
def auto_export_gltf(dummy):
    if bpy.context.scene.gltf_export_settings.auto_export_on_save:
        export_gltf(bpy.context)
    
def register():
    bpy.utils.register_class(GLTFExportSettings)
    bpy.types.Scene.gltf_export_settings = bpy.props.PointerProperty(type=GLTFExportSettings)
    
    bpy.utils.register_class(Blender2UnityPanel)
    bpy.utils.register_class(ExportGLTFOperator)
    
    # Remove previous handlers to avoid duplicates
    bpy.app.handlers.save_post[:] = [h for h in bpy.app.handlers.save_post if h.__name__ != "auto_export_gltf"]
    
    bpy.app.handlers.save_post.append(auto_export_gltf)

def unregister():
    bpy.utils.unregister_class(GLTFExportSettings)
    del bpy.types.Scene.gltf_export_settings
    
    bpy.utils.unregister_class(Blender2UnityPanel)
    bpy.utils.unregister_class(ExportGLTFOperator)
    
    bpy.app.handlers.save_post.remove(auto_export_gltf)

if __name__ == "__main__":
    register()
