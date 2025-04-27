# The . before means that you're performing a relative import.
# This is safe cos u wont have accidental collistions with other packages
from .splitVertexGroup import (
  kimjafasu_preprocess_split_vertex_groups,
  kimjafasu_postprocess_cleanup
)

def register():
    pass

def unregister():
    pass