import bpy

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