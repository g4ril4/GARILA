with open("ui.py", "r", encoding="utf-8") as f:
    code = f.read()

# 5. Add set_theme to MainWindow
main_win_set_theme = '''    def set_theme(self, hex_code: str, category_name: str = ""):
        """Dynamically fade entire UI palette to the requested theme hex."""
        if hasattr(self, "_theme_controller"):
            self._theme_controller.transition_to(hex_code)
            if category_name:
                self._log_sig.emit(f"SYS // THEME: {category_name} ({hex_code})")
'''
if "def set_theme(self" not in code:
    code = code.replace("class _RootShim:", main_win_set_theme + "\n\nclass _RootShim:", 1)
    print("Added set_theme to MainWindow")

# 6. Add set_theme to JarvisUI
jarvis_ui_set_theme = '''    def set_theme(self, hex_code: str, category_name: str = ""):
        self._win.set_theme(hex_code, category_name)
'''
if "def set_theme(self" not in code.split("class JarvisUI:")[1]:
    code = code.replace("    def start_speaking(self):", jarvis_ui_set_theme + "\n    def start_speaking(self):", 1)
    print("Added set_theme to JarvisUI")

with open("ui.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Patch UI step 1 finished successfully!")
