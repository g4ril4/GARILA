import re

with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update _paint_idle in _DropCanvas
old_idle = """    def _paint_idle(self, p, W, H, hover):
        cx, cy = W / 2, H / 2
        col = qcol(C.PRI_DIM if not hover else C.PRI)
        p.setPen(QPen(col, 2)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(QPointF(cx, cy - 14), QPointF(cx, cy + 4))
        p.drawLine(QPointF(cx - 8, cy - 6), QPointF(cx, cy - 14))
        p.drawLine(QPointF(cx + 8, cy - 6), QPointF(cx, cy - 14))
        p.drawLine(QPointF(cx - 14, cy + 4), QPointF(cx + 14, cy + 4))
        p.setFont(QFont("Courier New", 8))
        p.setPen(QPen(qcol(C.PRI_DIM if not hover else C.TEXT), 1))
        p.drawText(QRectF(0, cy + 8, W, 16), Qt.AlignmentFlag.AlignCenter,
                   "Drop file here  or  Click to Browse")
        p.setFont(QFont("Courier New", 7))
        p.setPen(QPen(qcol("#1a4a5a"), 1))
        p.drawText(QRectF(0, cy + 24, W, 14), Qt.AlignmentFlag.AlignCenter,
                   "Images · Video · Audio · PDF · Docs · Code · Data")"""

new_idle = """    def _paint_idle(self, p, W, H, hover):
        # Draw two cyber tray outline buttons matching reference image
        cx = W / 2.0
        cy = H / 2.0 - 8
        box_w, box_h = 42.0, 42.0
        gap = 20.0

        pri = qcol(C.PRI if hover else C.PRI_DIM)
        border = qcol(C.PRI if hover else C.BORDER)
        bg = qcol("#002834" if hover else "#00121b")

        # Box 1 (Left - Upload [ ↑ ])
        x1 = cx - box_w - gap / 2.0
        y1 = cy - box_h / 2.0
        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 1.2))
        p.drawRoundedRect(QRectF(x1, y1, box_w, box_h), 5, 5)

        # Tray 1 graphic
        p.setPen(QPen(pri, 1.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        # Tray outline
        p.drawLine(QPointF(x1 + 9, y1 + 25), QPointF(x1 + 9, y1 + 33))
        p.drawLine(QPointF(x1 + 9, y1 + 33), QPointF(x1 + 33, y1 + 33))
        p.drawLine(QPointF(x1 + 33, y1 + 33), QPointF(x1 + 33, y1 + 25))
        # Arrow pointing up
        p.drawLine(QPointF(x1 + 21, y1 + 26), QPointF(x1 + 21, y1 + 10))
        p.drawLine(QPointF(x1 + 15, y1 + 16), QPointF(x1 + 21, y1 + 10))
        p.drawLine(QPointF(x1 + 27, y1 + 16), QPointF(x1 + 21, y1 + 10))

        # Box 2 (Right - Download / Drop [ ↓ ])
        x2 = cx + gap / 2.0
        y2 = cy - box_h / 2.0
        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 1.2))
        p.drawRoundedRect(QRectF(x2, y2, box_w, box_h), 5, 5)

        # Tray 2 graphic
        p.setPen(QPen(pri, 1.8))
        p.setBrush(Qt.BrushStyle.NoBrush)
        # Tray outline
        p.drawLine(QPointF(x2 + 9, y2 + 25), QPointF(x2 + 9, y2 + 33))
        p.drawLine(QPointF(x2 + 9, y2 + 33), QPointF(x2 + 33, y2 + 33))
        p.drawLine(QPointF(x2 + 33, y2 + 33), QPointF(x2 + 33, y2 + 25))
        # Arrow pointing down
        p.drawLine(QPointF(x2 + 21, y2 + 10), QPointF(x2 + 21, y2 + 26))
        p.drawLine(QPointF(x2 + 15, y2 + 20), QPointF(x2 + 21, y2 + 26))
        p.drawLine(QPointF(x2 + 27, y2 + 20), QPointF(x2 + 21, y2 + 26))

        # Text below
        p.setFont(QFont("Courier New", 7, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.PRI if hover else C.TEXT_MED), 1))
        p.drawText(QRectF(0, H - 20, W, 14), Qt.AlignmentFlag.AlignCenter, "UPLOAD  ·  DROP FILE HERE")"""

assert old_idle in content, "old_idle not found"
content = content.replace(old_idle, new_idle, 1)

# 2. Update CyberPanel class
old_cyber_panel = """class CyberPanel(QFrame):
    \"\"\"Semi-transparent dark glass panel with glowing borders & cyber titlebar.\"\"\"
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("CyberPanel")
        self.setStyleSheet(f\"\"\"
            QFrame#CyberPanel {{
                background: rgba(4, 18, 28, 0.72);
                border: 1px solid {C.BORDER};
                border-radius: 6px;
            }}
        \"\"\")
        self.root_lay = QVBoxLayout(self)
        self.root_lay.setContentsMargins(6, 6, 6, 6)
        self.root_lay.setSpacing(4)

        # Header bar
        hdr = QHBoxLayout()
        hdr.setContentsMargins(4, 2, 4, 2)
        title_lbl = QLabel(f"◈  {title}")
        title_lbl.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; letter-spacing: 1px;")
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        ctrl_lbl = QLabel("_  □  ✕")
        ctrl_lbl.setFont(QFont("Courier New", 7))
        ctrl_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        hdr.addWidget(ctrl_lbl)
        self.root_lay.addLayout(hdr)"""

new_cyber_panel = """class CyberPanel(QFrame):
    \"\"\"Semi-transparent dark glass panel with glowing borders & cyber titlebar.\"\"\"
    def __init__(self, title: str, ctrl_text: str = "_  □  ✕", parent=None):
        super().__init__(parent)
        self.setObjectName("CyberPanel")
        self._title = title
        self._ctrl_text = ctrl_text
        self.setStyleSheet(f\"\"\"
            QFrame#CyberPanel {{
                background: rgba(3, 14, 24, 0.85);
                border: 1px solid {C.BORDER};
                border-radius: 6px;
            }}
        \"\"\")
        self.root_lay = QVBoxLayout(self)
        self.root_lay.setContentsMargins(6, 4, 6, 6)
        self.root_lay.setSpacing(4)

        # Header bar
        hdr = QHBoxLayout()
        hdr.setContentsMargins(4, 2, 4, 2)
        self._title_lbl = QLabel(f"◈  {title}")
        self._title_lbl.setFont(QFont("Courier New", 8, QFont.Weight.Bold))
        self._title_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; letter-spacing: 1px;")
        hdr.addWidget(self._title_lbl)
        hdr.addStretch()

        self._ctrl_lbl = QLabel(ctrl_text)
        self._ctrl_lbl.setFont(QFont("Courier New", 7))
        self._ctrl_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;")
        hdr.addWidget(self._ctrl_lbl)
        self.root_lay.addLayout(hdr)

    def refresh_theme(self):
        self.setStyleSheet(f\"\"\"
            QFrame#CyberPanel {{
                background: rgba(3, 14, 24, 0.85);
                border: 1px solid {C.BORDER};
                border-radius: 6px;
            }}
        \"\"\")
        if hasattr(self, "_title_lbl"):
            self._title_lbl.setStyleSheet(f"color: {C.PRI}; background: transparent; letter-spacing: 1px;")
        if hasattr(self, "_ctrl_lbl"):
            self._ctrl_lbl.setStyleSheet(f"color: {C.TEXT_DIM}; background: transparent;\")"""

assert old_cyber_panel in content, "old_cyber_panel not found"
content = content.replace(old_cyber_panel, new_cyber_panel, 1)

# 3. Add top-left cyber emblem & name in HudCanvas.paintEvent
old_hud_paint = """    def paintEvent(self, _):
        p = QPainter(self)
        if not p.isActive():      # device not ready (e.g. 0-size during layout) — skip cleanly
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), qcol(C.BG))

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        fw = min(W, H)

        # grid dots — blitted from a cached layer; rebuilt only when the size
        # or the theme's ghost colour changes (so live re-theming still works).
        _gkey = (W, H, C.PRI_GHO)
        if self._grid_cache is None or self._grid_key != _gkey:
            self._grid_cache = self._make_grid(W, H)
            self._grid_key   = _gkey
        p.drawPixmap(0, 0, self._grid_cache)"""

new_hud_paint = """    def paintEvent(self, _):
        p = QPainter(self)
        if not p.isActive():      # device not ready (e.g. 0-size during layout) — skip cleanly
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), qcol("#000000"))

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        fw = min(W, H)

        # grid dots — blitted from a cached layer; rebuilt only when the size
        # or the theme's ghost colour changes (so live re-theming still works).
        _gkey = (W, H, C.PRI_GHO)
        if self._grid_cache is None or self._grid_key != _gkey:
            self._grid_cache = self._make_grid(W, H)
            self._grid_key   = _gkey
        p.drawPixmap(0, 0, self._grid_cache)

        # Cyber emblem & assistant name at top-left (from reference image)
        p.save()
        p.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.PRI_DIM, 90), 3))
        p.drawText(QRectF(22, 18, 340, 36), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"◈  {self._assistant_name}")
        p.setPen(QPen(qcol(C.PRI), 1))
        p.drawText(QRectF(22, 18, 340, 36), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"◈  {self._assistant_name}")
        p.restore()"""

assert old_hud_paint in content, "old_hud_paint not found"
content = content.replace(old_hud_paint, new_hud_paint, 1)

# 4. In HudCanvas: make head slightly larger and prominent
old_head_r = """            _r_head = min(fw * 0.355, _band_h / (self._avatar.SPAN + 0.08))"""
new_head_r = """            _r_head = min(fw * 0.40, _band_h / (self._avatar.SPAN + 0.05))"""
if old_head_r in content:
    content = content.replace(old_head_r, new_head_r, 1)

# 5. In MainWindow.__init__: remove header and footer, setup cyber layout
old_mw_init = """        central = QWidget()
        central.setStyleSheet(f"background: {C.BG};")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(6, 6, 6, 6)
        body.setSpacing(8)"""

new_mw_init = """        central = QWidget()
        central.setStyleSheet("background: #000000;")
        self.setCentralWidget(central)

        # Subtle floating drawer button in top-right corner
        self._drawer_btn = QPushButton("⚙", central)
        self._drawer_btn.setFixedSize(24, 24)
        self._drawer_btn.setFont(QFont("Courier New", 10))
        self._drawer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._drawer_btn.setToolTip("Settings & Controls")
        self._drawer_btn.setStyleSheet(f\"\"\"
            QPushButton {{
                background: rgba(0, 20, 32, 0.6); color: {C.TEXT_DIM};
                border: 1px solid {C.BORDER}; border-radius: 4px;
            }}
            QPushButton:hover {{ color: {C.PRI}; border-color: {C.PRI_DIM}; background: {C.PRI_GHO}; }}
            QPushButton:checked {{ color: {C.PRI}; border-color: {C.PRI}; background: {C.PRI_GHO}; }}
        \"\"\")
        self._drawer_btn.setCheckable(True)
        self._drawer_btn.clicked.connect(self._toggle_drawer)
        self._drawer_btn.raise_()

        # Labels preserved for compatibility
        self._title_lbl = QLabel(_display)
        self._sub_lbl = QLabel("Advanced Tactical AI Assistant")
        self._clock_lbl = QLabel("")
        self._date_lbl = QLabel("")

        root = QVBoxLayout(central)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(10)"""

assert old_mw_init in content, "old_mw_init not found"
content = content.replace(old_mw_init, new_mw_init, 1)

# 6. Remove root.addWidget(self._build_footer()) and adjust stretch
old_mw_body = """        self._center_split.addWidget(self._hud_cam_stack)
        self._center_split.addWidget(self._content_panel)
        self._center_split.addWidget(self._quiz_panel)
        self._center_split.setStretchFactor(0, 3)
        self._center_split.setStretchFactor(1, 1)
        self._center_split.setCollapsible(0, False)
        body.addWidget(self._center_split, stretch=5)

        self._right_panel = self._build_right_panel()
        body.addWidget(self._right_panel, stretch=0)

        root.addLayout(body, stretch=1)
        root.addWidget(self._build_footer())"""

new_mw_body = """        self._center_split.addWidget(self._hud_cam_stack)
        self._center_split.addWidget(self._content_panel)
        self._center_split.addWidget(self._quiz_panel)
        self._center_split.setStretchFactor(0, 3)
        self._center_split.setStretchFactor(1, 1)
        self._center_split.setCollapsible(0, False)
        body.addWidget(self._center_split, stretch=10)

        self._right_panel = self._build_right_panel()
        body.addWidget(self._right_panel, stretch=11)

        root.addLayout(body, stretch=1)

        # Theme fade controller for 50 dynamic themes
        self._theme_controller = ThemeFadeController(self)
        self._theme_controller.theme_changed.connect(self._on_theme_changed)"""

assert old_mw_body in content, "old_mw_body not found"
content = content.replace(old_mw_body, new_mw_body, 1)

# 7. Update _build_right_panel
old_right_panel = """    def _build_right_panel(self) -> QWidget:
        w = QWidget()
        w.setMinimumWidth(560)
        w.setStyleSheet(f"background: {C.DARK}; border-left: 1px solid {C.BORDER};")
        root_lay = QVBoxLayout(w)
        root_lay.setContentsMargins(6, 6, 6, 6)
        root_lay.setSpacing(6)

        # ── Tactical Grid: Telemetry, Network Traffic, CPU Core | Activity Log, File Drop ──
        grid_w = QWidget()
        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        # 1. Telemetry Panel (Row 0, Col 0)
        self._panel_telemetry = CyberPanel("TELEMETRY")
        self._telemetry_widget = TelemetryWaveWidget()
        self._panel_telemetry.root_lay.addWidget(self._telemetry_widget)
        grid.addWidget(self._panel_telemetry, 0, 0)

        # 2. Activity Log Panel (Row 0 & 1, Col 1) -> Tall cyber console!
        self._panel_log = CyberPanel("ACTIVITY LOG")
        self._log = LogWidget()
        self._panel_log.root_lay.addWidget(self._log)
        grid.addWidget(self._panel_log, 0, 1, 2, 1)

        # 3. Network Traffic Panel (Row 1, Col 0)
        self._panel_net = CyberPanel("NETWORK TRAFFIC")
        self._net_traffic_widget = NetworkTrafficWidget()
        self._panel_net.root_lay.addWidget(self._net_traffic_widget)
        grid.addWidget(self._panel_net, 1, 0)

        # 4. CPU Core Panel (Row 2, Col 0)
        self._panel_cpu = CyberPanel("CPU CORE")
        self._cpu_core_widget = CpuCoreWidget()
        self._panel_cpu.root_lay.addWidget(self._cpu_core_widget)
        grid.addWidget(self._panel_cpu, 2, 0)

        # 5. File Drop Panel (Row 2, Col 1)
        self._panel_drop = CyberPanel("FILE DROP")
        self._drop_zone = FileDropZone()
        self._drop_zone.file_selected.connect(self._on_file_selected)
        self._panel_drop.root_lay.addWidget(self._drop_zone)
        grid.addWidget(self._panel_drop, 2, 1)

        root_lay.addWidget(grid_w, stretch=1)

        # 6. Message Input Panel (Bottom - spans full right width)
        self._panel_input = CyberPanel("MESSAGE INPUT")"""

new_right_panel = """    def _build_right_panel(self) -> QWidget:
        w = QWidget()
        w.setMinimumWidth(560)
        w.setObjectName("RightTacticalConsole")
        w.setStyleSheet(f\"\"\"
            QWidget#RightTacticalConsole {{
                background: rgba(2, 10, 18, 0.88);
                border: 1px solid {C.BORDER};
                border-radius: 8px;
            }}
        \"\"\")
        root_lay = QVBoxLayout(w)
        root_lay.setContentsMargins(8, 8, 8, 8)
        root_lay.setSpacing(8)

        # ── Tactical Grid: Telemetry, Network Traffic, CPU Core | Activity Log, File Drop ──
        grid_w = QWidget()
        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout(grid_w)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        # 1. Telemetry Panel (Row 0, Col 0)
        self._panel_telemetry = CyberPanel("TELEMETRY", ctrl_text="_  □  ✕")
        self._telemetry_widget = TelemetryWaveWidget()
        self._panel_telemetry.root_lay.addWidget(self._telemetry_widget)
        grid.addWidget(self._panel_telemetry, 0, 0)

        # 2. Activity Log Panel (Row 0 & 1, Col 1) -> Tall cyber console!
        self._panel_log = CyberPanel("ACTIVITY LOG", ctrl_text=">  _  □  ✕")
        self._log = LogWidget()
        self._panel_log.root_lay.addWidget(self._log)
        grid.addWidget(self._panel_log, 0, 1, 2, 1)

        # 3. Network Traffic Panel (Row 1, Col 0)
        self._panel_net = CyberPanel("NETWORK TRAFFIC", ctrl_text="_  □  ✕")
        self._net_traffic_widget = NetworkTrafficWidget()
        self._panel_net.root_lay.addWidget(self._net_traffic_widget)
        grid.addWidget(self._panel_net, 1, 0)

        # 4. CPU Core Panel (Row 2, Col 0)
        self._panel_cpu = CyberPanel("CPU CORE", ctrl_text="✕")
        self._cpu_core_widget = CpuCoreWidget()
        self._panel_cpu.root_lay.addWidget(self._cpu_core_widget)
        grid.addWidget(self._panel_cpu, 2, 0)

        # 5. File Drop Panel (Row 2, Col 1)
        self._panel_drop = CyberPanel("FILE DROP", ctrl_text="✕")
        self._drop_zone = FileDropZone()
        self._drop_zone.file_selected.connect(self._on_file_selected)
        self._panel_drop.root_lay.addWidget(self._drop_zone)
        grid.addWidget(self._panel_drop, 2, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)

        root_lay.addWidget(grid_w, stretch=1)

        # 6. Message Input Panel (Bottom - spans full right width)
        self._panel_input = CyberPanel("MESSAGE INPUT", ctrl_text="_  □  ✕")"""

assert old_right_panel in content, "old_right_panel not found"
content = content.replace(old_right_panel, new_right_panel, 1)

# 8. Add _on_theme_changed to MainWindow
theme_handler = """    def _on_theme_changed(self, hex_col: str):
        if hasattr(self, 'hud'):
            self.hud.update()
        if hasattr(self, '_panel_telemetry'):
            self._panel_telemetry.refresh_theme()
        if hasattr(self, '_panel_net'):
            self._panel_net.refresh_theme()
        if hasattr(self, '_panel_cpu'):
            self._panel_cpu.refresh_theme()
        if hasattr(self, '_panel_log'):
            self._panel_log.refresh_theme()
        if hasattr(self, '_panel_drop'):
            self._panel_drop.refresh_theme()
        if hasattr(self, '_panel_input'):
            self._panel_input.refresh_theme()
        if hasattr(self, '_drop_zone'):
            self._drop_zone.update()
        if hasattr(self, '_mute_btn'):
            self._style_mute_btn()

    def set_theme(self, hex_code: str, category_name: str = ""):"""

content = content.replace("    def set_theme(self, hex_code: str, category_name: str = \"\"):""", theme_handler, 1)

# 9. Update resizeEvent for _drawer_btn
old_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()"""

new_resize = """    def resizeEvent(self, event):
        super().resizeEvent(event)
        cw = self.centralWidget()
        if hasattr(self, '_drawer_btn'):
            self._drawer_btn.setGeometry(cw.width() - 34, 12, 22, 22)
            self._drawer_btn.raise_()"""

assert old_resize in content, "old_resize not found"
content = content.replace(old_resize, new_resize, 1)

# 10. Update _position_quick_drawer
old_drawer_pos = """    def _position_quick_drawer(self):
        if not hasattr(self, '_quick_drawer'):
            return
        _W = 220
        self._quick_drawer.setFixedWidth(_W)
        self._quick_drawer.adjustSize()
        self._quick_drawer.setGeometry(12, 54, _W, self._quick_drawer.sizeHint().height())"""

new_drawer_pos = """    def _position_quick_drawer(self):
        if not hasattr(self, '_quick_drawer'):
            return
        cw = self.centralWidget()
        _W = 220
        self._quick_drawer.setFixedWidth(_W)
        self._quick_drawer.adjustSize()
        self._quick_drawer.setGeometry(cw.width() - _W - 12, 38, _W, self._quick_drawer.sizeHint().height())"""

assert old_drawer_pos in content, "old_drawer_pos not found"
content = content.replace(old_drawer_pos, new_drawer_pos, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: UI Redesign applied cleanly.")
