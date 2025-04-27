import bpy

from . import utils

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
        
        errors = utils.kimjafasu_get_export_errors(settings)

        if errors:
            for msg in errors:
                layout.label(text=msg, icon='ERROR')
        else:
            if (settings.auto_export_on_save == False):
                layout.operator("export_scene.gltf_manual", text="Manual Export", icon='GHOST_ENABLED')
        
      