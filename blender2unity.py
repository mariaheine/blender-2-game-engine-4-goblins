import bpy
import os

class GLTFExportSettings(bpy.types.PropertyGroup):
    export_dir: bpy.props.StringProperty(
        name="Export To",
        description="🕊️ Directory where the GLTF file will be saved",
        default="/path_where_export/",  # Default relative to blend file
        subtype='DIR_PATH',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    )
    
    apply_transforms: bpy.props.BoolProperty(
        name="Apply Transforms",
        description="Apply object transformations before exporting",
        default=False
    )
    
    export_format: bpy.props.EnumProperty(
        name="Format",
        description="Choose export format",
        items=[
            ('GLB', "GLB (Binary)", "Exports a single .glb file"),
            ('GLTF_SEPARATE', "GLTF + BIN", "Exports separate .gltf and .bin files"),
            ('FBX', "FBX", "Exports as .fbx bleh proprietary file format")
        ],
        default='GLTF_SEPARATE'
    )

    auto_export_on_save: bpy.props.BoolProperty(
        name="Auto-Export on Save",
        description="Automatically export when saving the .blend file",
        default=True
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
        
        layout.separator()  # Adds some spacing
        
        # Export Directory Path
        layout.prop(scene.gltf_export_settings, "export_dir", icon='EXPORT')
        
        # Dropdown for export format
        layout.prop(scene.gltf_export_settings, "export_format", icon='SHADERFX') 
        
        layout.separator() 
        layout.label(text="Tweaks:")
        
        # Apply Transforms Checkbox
        layout.prop(scene.gltf_export_settings, "apply_transforms", icon='SCENE_DATA')
        
        # Toggle Auto Export
        layout.prop(scene.gltf_export_settings, "auto_export_on_save", icon='RNA')  
        
        #layout.row().label(text="---------" * 10, icon="INFO")
        layout.separator()
        
        row = layout.row()
        row.operator("export_scene.gltf_manual", text="Export!", icon='GHOST_ENABLED')


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
    apply_transforms = context.scene.gltf_export_settings.apply_transforms
    
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
        bpy.ops.export_scene.gltf(
            filepath=export_path,
            export_format=export_format,
            use_selection=True,
            export_apply=apply_transforms,
            export_yup=True
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
