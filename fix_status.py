with open('ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        if self._avatar is not None and self.hud_style == "face":
            _band_t = 20.0"""
replacement = """        _sy_status = H - 24.0
        if self._avatar is not None and self.hud_style == "face":
            _band_t = 20.0"""

assert target in text
text = text.replace(target, replacement, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Fixed _sy_status definition.")
