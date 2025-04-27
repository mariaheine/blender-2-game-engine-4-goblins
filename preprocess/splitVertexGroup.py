import bpy

def kimjafasu_preprocess_split_vertex_groups(context, objects_to_be_exported):
    temp_objects = []
    
    for obj in objects_to_be_exported:
        if obj.type == 'MESH' and "Vertex" in obj.vertex_groups.keys():
            # Duplicate the object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()
            dup_obj = context.active_object
            temp_objects.append(dup_obj)
            
            # Go to edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Select vertices in the "Vertex" group
            bpy.ops.object.vertex_group_set_active(group="Vertex")
            bpy.ops.object.vertex_group_select()
            
            # Separate selected vertices into a new object
            bpy.ops.mesh.separate(type='SELECTED')
            
            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
    
    return temp_objects
  
def kimjafasu_postprocess_cleanup(temp_objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_objects:
        if obj and obj.name in bpy.data.objects:
            obj.select_set(True)
    bpy.ops.object.delete()

