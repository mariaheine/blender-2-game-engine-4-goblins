# The . before means that you're performing a relative import.
# This is safe cos u wont have accidental collistions with other packages
from .ui_common import (
  kimjafasu_refresh_ui,
  kimjafasu_split_text
)
from .logging import (
  kimjafasu_log_message,
  kimjafasu_console_print
)

def register():
    pass

def unregister():
    pass