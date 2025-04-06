import bpy

def kimjafasu_refresh_ui():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':  # or 'PROPERTIES', etc.
                area.tag_redraw()
                
def kimjafasu_split_text(text, max_length=50):
    lines = []
    while len(text) > max_length:
        split_point = text.rfind(" ", 0, max_length)
        if split_point == -1:
            split_point = max_length
        lines.append(text[:split_point])
        text = text[split_point:].lstrip()
    lines.append(text)
    return lines