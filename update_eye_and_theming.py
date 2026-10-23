import re

# ── 1. Update cyber_eye.py ───────────────────────────────────────────────────
with open('cyber_eye.py', 'r', encoding='utf-8') as f:
    eye_code = f.read()

# Replace hardcoded base_r with a well-scaled radius so the eye fits 100% on screen
old_eye_paint_head = '''        cx, cy = W * 0.48, H * 0.50
        base_r = min(W * 0.42, H * 0.42)

        # Dynamic Cyber Violet & Neon Cyan Colors matching media_1792674303275_e4416d9f.jpg
        col_cyan   = QColor("#00F0FF")
        col_violet = QColor("#BD00FF")
        col_blue   = QColor("#0088FF")
        col_white  = QColor("#FFFFFF")
        amp = self._amp_disp'''

new_eye_paint_head = '''        cx, cy = W * 0.50, H * 0.50
        # Scaled to fit completely inside the panel with generous margins on all sides
        base_r = min(W * 0.22, H * 0.27)

        # Dynamically linked to active theme palette
        try:
            from ui import C
            col_violet = QColor(getattr(C, "PRI", "#BD00FF"))
            col_cyan   = QColor(getattr(C, "ACC", "#00F0FF"))
            col_blue   = QColor(getattr(C, "BORDER_B", "#0088FF"))
        except Exception:
            col_violet = QColor("#BD00FF")
            col_cyan   = QColor("#00F0FF")
            col_blue   = QColor("#0088FF")

        col_white  = QColor("#FFFFFF")
        amp = self._amp_disp'''

assert old_eye_paint_head in eye_code, "old_eye_paint_head not found"
eye_code = eye_code.replace(old_eye_paint_head, new_eye_paint_head, 1)

with open('cyber_eye.py', 'w', encoding='utf-8') as f:
    f.write(eye_code)
print("cyber_eye.py updated: resized to fit perfectly & dynamically linked to C theme palette.")

# ── 2. Update main.py to trigger theme on voice speech & response ─────────────
with open('main.py', 'r', encoding='utf-8') as f:
    main_code = f.read()

old_full_in_block = '''                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self._last_out_logged = ""   # new exchange
                                self.ui.write_log(f"You: {full_in}")'''

new_full_in_block = '''                            full_in = " ".join(in_buf).strip()
                            if full_in:
                                self._last_out_logged = ""   # new exchange
                                self.ui.write_log(f"You: {full_in}")
                                try:
                                    _preset = classify_text_theme(full_in)
                                    if _preset:
                                        self.ui.set_theme(_preset.hex_code, _preset.name_ku)
                                except Exception:
                                    pass'''

assert old_full_in_block in main_code, "old_full_in_block not found"
main_code = main_code.replace(old_full_in_block, new_full_in_block, 1)

old_full_out_block = '''                                try:
                                    _preset = classify_text_theme(full_out)
                                    if _preset and _preset.key != "tech":
                                        self.ui.set_theme(_preset.hex_code, _preset.name_ku)
                                except Exception:
                                    pass'''

new_full_out_block = '''                                try:
                                    _preset = classify_text_theme(full_out)
                                    if _preset:
                                        self.ui.set_theme(_preset.hex_code, _preset.name_ku)
                                except Exception:
                                    pass'''

assert old_full_out_block in main_code, "old_full_out_block not found"
main_code = main_code.replace(old_full_out_block, new_full_out_block, 1)

with open('main.py', 'w', encoding='utf-8') as f:
    f.write(main_code)
print("main.py updated: voice speech now triggers instant theme shift.")
