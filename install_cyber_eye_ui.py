import re
import json

# 1. Update config/api_keys.json to #BD00FF (Neon Violet / Magenta)
try:
    with open('config/api_keys.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    cfg['ui_color'] = '#BD00FF'
    with open('config/api_keys.json', 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)
    print("config/api_keys.json ui_color updated to #BD00FF.")
except Exception as e:
    print("Could not update config/api_keys.json:", e)

# 2. Update ui.py to use CyberEyeCanvas
with open('ui.py', 'r', encoding='utf-8') as f:
    ui_code = f.read()

# Add import of CyberEyeCanvas
if "from cyber_eye import CyberEyeCanvas" not in ui_code:
    ui_code = ui_code.replace("from core.avatar import HoloAvatar", "from core.avatar import HoloAvatar\nfrom cyber_eye import CyberEyeCanvas", 1)

# In MainWindow.__init__: replace self.hud = HudCanvas(...) with self.hud = CyberEyeCanvas(...)
ui_code = ui_code.replace("self.hud = HudCanvas(face_path, _display)", "self.hud = CyberEyeCanvas(face_path, _display)", 1)

# Update C palette to match the Cyber Violet & Cyan aesthetic of media_1792674303275_e4416d9f.jpg
old_c_class = '''class C:
    BG        = "#000000"
    PANEL     = "#020e1a"
    PANEL2    = "#031424"
    BORDER    = "#0a3c5a"
    BORDER_B  = "#00a8d6"
    BORDER_A  = "#0080aa"
    PRI       = "#00F0FF"      # Pure Neon Electric Cyan!
    PRI_DIM   = "#0099cc"      # Deep Electric Cyan
    PRI_GHO   = "#002438"      # Translucent Cyber Cyan Ghost
    ACC       = "#00E5FF"      # Vivid Cyan Glow
    ACC2      = "#00b4d8"      # Cyan Secondary
    GREEN     = "#00ffaa"
    GREEN_D   = "#00bb77"
    RED       = "#ff3355"
    MUTED_C   = "#ff3366"
    TEXT      = "#b8f4ff"      # Ice Cyan White
    TEXT_DIM  = "#4a8a9e"      # Dim Cyber Cyan
    TEXT_MED  = "#70c4db"      # Medium Cyan
    WHITE     = "#eafaff"      # Pure Bright Cyan-White
    DARK      = "#010a12"      # Ultra Deep Black-Blue
    BAR_BG    = "#021220"      # Cyber Bar Dark Blue'''

new_c_class = '''class C:
    BG        = "#000000"
    PANEL     = "#0c0216"
    PANEL2    = "#140422"
    BORDER    = "#440066"
    BORDER_B  = "#BD00FF"
    BORDER_A  = "#8800cc"
    PRI       = "#BD00FF"      # Neon Electric Violet / Magenta!
    PRI_DIM   = "#7700aa"      # Deep Cyber Violet
    PRI_GHO   = "#220038"      # Translucent Violet Ghost
    ACC       = "#00F0FF"      # Electric Cyan Glow
    ACC2      = "#E024C3"      # Vivid Magenta
    GREEN     = "#00ffcc"
    GREEN_D   = "#00aa88"
    RED       = "#ff3355"
    MUTED_C   = "#ff3366"
    TEXT      = "#f0d4ff"      # Soft Violet-White
    TEXT_DIM  = "#7a489e"      # Dim Violet
    TEXT_MED  = "#b07cdb"      # Medium Violet
    WHITE     = "#ffffff"      # Pure Bright White
    DARK      = "#080110"      # Ultra Deep Violet-Black
    BAR_BG    = "#12021e"      # Cyber Bar Dark Violet'''

if old_c_class in ui_code:
    ui_code = ui_code.replace(old_c_class, new_c_class, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(ui_code)

print("ui.py successfully updated with CyberEyeCanvas and Cyber Violet / Cyan palette.")
