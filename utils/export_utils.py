import bpy
         
def kimjafasu_get_export_errors(settings):
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
  
def kimjafasu_cleanup_after(export_target, original_selected_objects, original_mode):
  # 🪶 Restore previous object selection
      if export_target != 'Selection':
          bpy.ops.object.select_all(action='DESELECT')
          for obj in original_selected_objects:
              obj.select_set(True)
          
      # Restore original mode
      if original_mode != 'OBJECT':
          bpy.ops.object.mode_set(mode=original_mode)