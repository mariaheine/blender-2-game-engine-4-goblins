import bpy
import os

class GLTFExportSettings(bpy.types.PropertyGroup):
    export_dir: bpy.props.StringProperty(
        name="Export Directory",
        description="Directory where the GLTF file will be saved",
        default="/path_where_export/",  # Default relative to blend file
        subtype='DIR_PATH',
        update=lambda self, context: context.area.tag_redraw()  # Force UI refresh
    )

class GLTFExportPanel(bpy.types.Panel):
    """Creates a Panel in the Object Properties N-Panel"""
    bl_label = "🕊️ Unity Exporter"
    bl_idname = "OBJECT_PT_gltf_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '‍🕊️ Uni Exp'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Export Directory Path
        layout.prop(scene.gltf_export_settings, "export_dir")

        # Export Button
        layout.operator("export_scene.gltf_manual")

class ExportGLTFOperator(bpy.types.Operator):
    """Export Selected Meshes to GLTF"""
    bl_idname = "export_scene.gltf_manual"
    bl_label = "Export GLTF"

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

    export_path = os.path.join(export_dir, blend_name + ".gltf")

    # Select only mesh objects
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            obj.select_set(True)

    # Export GLTF with coordinate system fix
    bpy.ops.export_scene.gltf(
        filepath=export_path,
        export_format='GLTF_SEPARATE',  # Options: GLB, GLTF_SEPARATE
        use_selection=True,  # Export only selected objects
        export_apply=True,   # Apply transforms
        export_yup=True      # Convert Blender Z-up to Unity Y-up
    )

    print(f"✅ GLTF Exported to: {export_path}")

# Register event: Auto-export on save
def auto_export_gltf(dummy):
    export_gltf(bpy.context)

# Register classes
def register():
    bpy.utils.register_class(GLTFExportSettings)
    bpy.types.Scene.gltf_export_settings = bpy.props.PointerProperty(type=GLTFExportSettings)

    bpy.utils.register_class(GLTFExportPanel)
    bpy.utils.register_class(ExportGLTFOperator)
    
    bpy.app.handlers.save_post.append(auto_export_gltf)

def unregister():
    bpy.utils.unregister_class(GLTFExportSettings)
    del bpy.types.Scene.gltf_export_settings

    bpy.utils.unregister_class(GLTFExportPanel)
    bpy.utils.unregister_class(ExportGLTFOperator)
    
    bpy.app.handlers.save_post.remove(auto_export_gltf)

if __name__ == "__main__":
    register()
