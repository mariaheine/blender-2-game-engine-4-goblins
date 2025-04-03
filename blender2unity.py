import bpy
import os

class GLTFExportSettings(bpy.types.PropertyGroup):
    export_dir: bpy.props.StringProperty(
        name="Export Dir",
        description="🕊️ Directory where the GLTF file will be saved",
        default="/path_where_export/",  # Default relative to blend file
        subtype='DIR_PATH',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    )
    
    apply_transforms: bpy.props.BoolProperty(
        name="Apply Transforms",
        description="Apply object transformations before exporting",
        default=True  # Checked by default
    )
    
    export_format: bpy.props.EnumProperty(
        name="Export Format",
        description="Choose export format",
        items=[
            ('GLB', "GLB (Binary)", "Exports a single .glb file"),
            ('GLTF_SEPARATE', "GLTF + BIN", "Exports separate .gltf and .bin files"),
            ('FBX', "FBX", "Exports as .fbx bleh proprietary file format")
        ],
        default='GLTF_SEPARATE'  # Default to GLB
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
        
        # Simple button in the toolbar
        row = layout.row()
        row.label(text="Hello from Blender Toolbar!")        


        layout.label(text="Export Settings:")
        
        # Export Directory Path
        layout.prop(scene.gltf_export_settings, "export_dir")
        
        # Apply Transforms Checkbox
        layout.prop(scene.gltf_export_settings, "apply_transforms")
        
        # Dropdown for export format
        layout.prop(scene.gltf_export_settings, "export_format")  
        
        row = layout.row()
        row.operator("export_scene.gltf_manual", text="Export!")  # Just a simple button to quit Blender


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
    
    if export_format == 'GLB':
        file_extension = ".glb"
    elif export_format == 'GLTF_SEPARATE':
        file_extension = ".gltf"
    elif export_format == 'FBX':
        file_extension = ".fbx"
    
    export_path = os.path.join(export_dir, blend_name + file_extension)

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

    print(f"✅ GLTF Exported to: {export_path}")
    
def register():
    bpy.utils.register_class(GLTFExportSettings)
    bpy.types.Scene.gltf_export_settings = bpy.props.PointerProperty(type=GLTFExportSettings)
    
    bpy.utils.register_class(Blender2UnityPanel)
    bpy.utils.register_class(ExportGLTFOperator)

def unregister():
    bpy.utils.unregister_class(GLTFExportSettings)
    del bpy.types.Scene.gltf_export_settings
    
    bpy.utils.unregister_class(Blender2UnityPanel)
    bpy.utils.unregister_class(ExportGLTFOperator)

if __name__ == "__main__":
    register()
