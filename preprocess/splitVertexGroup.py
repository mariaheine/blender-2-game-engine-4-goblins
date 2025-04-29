import bpy

def kimjafasu_preprocess_split_vertex_groups(context, objects_to_be_exported):

    # Before separate
    pre_objects = set(bpy.context.scene.objects)
    process_objects = pre_objects
    
    split_objects = []

    for obj in objects_to_be_exported:
        if obj.type == 'MESH' and "Vertex" in obj.vertex_groups.keys():
            split_objects.append(obj)
            # Duplicate the object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            context.view_layer.objects.active = obj
            bpy.ops.object.duplicate()
            duplicate = context.active_object  # <- correct, it's the duplicated one
            duplicate.name = f"{obj.name}.base"
            
            # Go to edit mode
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='DESELECT')
            
            # Select vertices in the "Vertex" group
            bpy.ops.object.vertex_group_set_active(group="Vertex")
            bpy.ops.object.vertex_group_select()
            
            # Separate selected vertices into a new object
            bpy.ops.mesh.separate(type='SELECTED')
            
            # Find reference and rename the newly created object
            post_separation_objects = set(context.scene.objects)
            temp_new_objects = post_separation_objects - process_objects
            for o in temp_new_objects:
              if (o is not duplicate):
                  o.name = f"{obj.name}.vertex"
            
            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')
            
            # Now immediately delete the duplicated original
            bpy.ops.object.select_all(action='DESELECT')
            
            process_objects = set(context.scene.objects)
    
    # After separate
    post_separation_objects = set(bpy.context.scene.objects)

    # Find the newly created objects
    new_objects = post_separation_objects - pre_objects

    # Now you have the new separated objects
    for obj in new_objects:
        print("New separated object:", obj.name)
    
    return split_objects, list(new_objects)
  
def kimjafasu_postprocess_cleanup(temp_objects):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in temp_objects:
        if obj and obj.name in bpy.data.objects:
            obj.select_set(True)
    bpy.ops.object.delete()

