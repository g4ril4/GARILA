with open('ui.py', 'r', encoding='utf-8') as f:
    text = f.read()

target = """        else:
            self._mute_btn.setText("🎙  MIC ON  —  کلیک بکە بۆ داخستن")
            self._mute_btn.setStyleSheet(f\"\"\"
                QPushButton {{
                    background: #001a0d; color: {C.GREEN};
                    border: 2px solid {C.GREEN}; border-radius: 6px;
                    font-size: 10px;
                }}
                QPushButton:hover {{
                    background: #002615; border-color: #00ffb0;
                    color: #00ffb0;
                }}
            \"\"\")"""

replacement = """        else:
            self._mute_btn.setText("🎙  MIC ON  —  کلیک بکە بۆ داخستن")
            self._mute_btn.setStyleSheet(f\"\"\"
                QPushButton {{
                    background: rgba(0, 24, 38, 0.9); color: #00f0ff;
                    border: 2px solid #00f0ff; border-radius: 6px;
                    font-size: 10px; font-weight: bold;
                }}
                QPushButton:hover {{
                    background: rgba(0, 42, 64, 0.95); border-color: #ffffff;
                    color: #ffffff;
                }}
            \"\"\")"""

assert target in text
text = text.replace(target, replacement, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated _style_mute_btn to Neon Cyan.")
