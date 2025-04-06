from datetime import datetime
from . import kimjafasu_split_text

# gosh multilines, why so hard, try this onetime: https://b3d.interplanety.org/en/multiline-text-in-blender-interface-panels/
def kimjafasu_log_message(self, text, level='INFO'):
    now = datetime.now().strftime("%H:%M:%S")
    text = f"[{now}] {text}"
    
    kimjafasu_console_print(text, level)
    
    lines = []
    if(len(text)) > 50:
        lines = kimjafasu_split_text(text, 50)
    else:
        lines.append(text)
    
    for index, line in enumerate(lines):
        msg = self.messages.add()
        msg.text = line
        if index != 0:
            level = 'NEWLINE'
        msg.level = level
        
def kimjafasu_console_print(text, level):
    if level == 'INFO':
      prefix = f"🕊️  [INFO @{__name__}]"
    elif level == 'WARNING':
      prefix = f"⚔️  [WARNING @{__name__}"
    elif level == 'ERROR':
      prefix = f"🔥 [ERROR @{__name__}]"
    else:
      prefix = ""
    print(f"{prefix} {text}")