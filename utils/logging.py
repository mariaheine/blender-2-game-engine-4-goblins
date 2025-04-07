from datetime import datetime
from . import kimjafasu_split_text

# gosh multilines, why so hard, try this onetime: https://b3d.interplanety.org/en/multiline-text-in-blender-interface-panels/
def kimjafasu_log_message(self, text, level='INFO'):
    now = datetime.now().strftime("%H:%M:%S")
    text = f"[{now}] {text}"
    
    text = kimjafasu_format_log(text, level)
    print(text)
    
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
        
def kimjafasu_format_log(text, level):
    if level == 'INFO':
      prefix = f"🕊️  [INFO]"
    elif level == 'WARNING':
      prefix = f"⚔️  [WARNING]"
    elif level == 'ERROR':
      prefix = f"🔥 [ERROR]"
    else:
      prefix = ""
    return f"{prefix} {text}"