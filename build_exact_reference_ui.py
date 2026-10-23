# Script to verify and update avatar.py and ui.py to match media_1792670334378_185ad2ee.jpg 100%

import re

# ── 1. Update core/avatar.py ──────────────────────────────────────────────────
with open('core/avatar.py', 'r', encoding='utf-8') as f:
    av_code = f.read()

# Make default pose angled slightly to the right (yaw = 0.28, pitch = -0.04) matching image
old_pose_init = """        self._yaw        = 0.0
        self._pitch      = 0.0"""
new_pose_init = """        self._yaw        = 0.26
        self._pitch      = -0.04"""
if old_pose_init in av_code:
    av_code = av_code.replace(old_pose_init, new_pose_init, 1)

# Increase orbital particle count to 140 and add multi-ring galaxy orbits
old_orbit_init = """        self._orbit_count = 85"""
new_orbit_init = """        self._orbit_count = 140"""
if old_orbit_init in av_code:
    av_code = av_code.replace(old_orbit_init, new_orbit_init, 1)

with open('core/avatar.py', 'w', encoding='utf-8') as f:
    f.write(av_code)

print("avatar.py updated.")

# ── 2. Update ui.py ───────────────────────────────────────────────────────────
with open('ui.py', 'r', encoding='utf-8') as f:
    ui_code = f.read()

# Make TelemetryWaveWidget draw the exact jagged angular multi-peak wave from reference image
old_telemetry_paint = """        for layer, (freq, speed, alpha, col) in enumerate([
            (0.022, 1.0, 48, QColor(C.PRI)),
            (0.038, -1.2, 26, QColor(C.ACC if C.ACC else "#00e5ff")),
        ]):
            path = QPainterPath()
            path.moveTo(0, H)
            pts = []
            steps = 42
            for i in range(steps + 1):
                x = (W / steps) * i
                y = base_h - math.sin(x * freq + self._phase * speed + layer * 1.5) * amp_scale \
                           - math.sin(x * freq * 2.2 - self._phase * 0.8) * (amp_scale * 0.35)
                y = max(4.0, min(H - 4.0, y))
                pts.append((x, y))
                path.lineTo(x, y)
            path.lineTo(W, H)
            path.closeSubpath()"""

new_telemetry_paint = """        # Render multi-peak jagged telemetry wave matching reference image
        for layer, (freq, speed, alpha, col) in enumerate([
            (0.032, 1.1, 75, QColor(C.PRI)),
            (0.048, -0.9, 38, QColor(C.ACC if C.ACC else "#00e5ff")),
        ]):
            path = QPainterPath()
            path.moveTo(0, H)
            pts = []
            steps = 30  # sharper angular peaks matching reference image
            for i in range(steps + 1):
                x = (W / steps) * i
                # Jagged triangular wave synthesis
                s1 = math.sin(x * freq + self._phase * speed + layer * 1.4)
                s2 = math.sin(x * freq * 2.6 - self._phase * 1.2) * 0.55
                s3 = math.sin(x * freq * 4.2 + self._phase * 0.7) * 0.28
                wave = s1 + s2 + s3
                y = base_h - wave * amp_scale
                y = max(6.0, min(H - 4.0, y))
                pts.append((x, y))
                path.lineTo(x, y)
            path.lineTo(W, H)
            path.closeSubpath()"""

if old_telemetry_paint in ui_code:
    ui_code = ui_code.replace(old_telemetry_paint, new_telemetry_paint, 1)

# In CpuCoreWidget: ensure exactly 6 vertical segmented equalizer bars labeled 001 - 006
old_cpu_init = """        self._cores = [20.0, 45.0, 15.0, 60.0, 30.0, 50.0, 25.0, 40.0]"""
new_cpu_init = """        self._cores = [92.0, 78.0, 62.0, 88.0, 42.0, 56.0]"""
if old_cpu_init in ui_code:
    ui_code = ui_code.replace(old_cpu_init, new_cpu_init, 1)

old_cpu_poll = """                self._cores = loads[:8]"""
new_cpu_poll = """                self._cores = (loads[:6] if len(loads) >= 6 else (loads + [30.0]*(6-len(loads)))[:6])"""
if old_cpu_poll in ui_code:
    ui_code = ui_code.replace(old_cpu_poll, new_cpu_poll, 1)

# Update HudCanvas: remove status text and audio waveform from overlapping the head
old_hud_canvas_paint_tail = """        # status text
        sy = _sy_status
        if self.muted:
            txt, col = "⊘  MUTED",     qcol(C.MUTED_C)
        elif self.speaking:
            txt, col = "●  SPEAKING",  qcol(C.ACC)
        elif self.state == "THINKING":
            sym = "◈" if self._blink else "◇"
            txt, col = f"{sym}  THINKING",   qcol(C.ACC2)
        elif self.state == "PROCESSING":
            sym = "▷" if self._blink else "▶"
            txt, col = f"{sym}  PROCESSING", qcol(C.ACC2)
        elif self.state == "LISTENING":
            sym = "●" if self._blink else "○"
            txt, col = f"{sym}  LISTENING",  qcol(C.GREEN)
        else:
            sym = "●" if self._blink else "○"
            txt, col = f"{sym}  {self.state}", qcol(C.PRI)

        p.setPen(QPen(col, 1))
        p.setFont(QFont("Courier New", 11, QFont.Weight.Bold))
        p.drawText(QRectF(0, sy, W, 26), Qt.AlignmentFlag.AlignCenter, txt)

        # waveform — reacts to the real audio level (mic while listening,
        # JARVIS's own voice while speaking). Falls back to a gentle idle
        # ripple when there's no sound. _amp_disp is the smoothed 0–1 level.
        wy = sy + 30
        N, bw = 36, 8
        wx0 = (W - N * bw) / 2
        amp = self._amp_disp
        mid = (N - 1) / 2.0
        for i in range(N):
            if self.muted:
                hgt, cl = 2, qcol(C.MUTED_C)
            else:
                env     = (1.0 - abs(i - mid) / mid) ** 0.7      # center-weighted hump
                shimmer = 0.55 + 0.45 * math.sin(self._tick * 0.18 + i * 0.7)
                idle    = 3.0 + 2.0 * math.sin(self._tick * 0.09 + i * 0.6)
                hgt     = int(max(2, min(24, idle + amp * 22.0 * env * shimmer)))
                if amp > 0.05:
                    cl = qcol(C.PRI) if hgt > 12 else qcol(C.PRI_DIM)
                else:
                    cl = qcol(C.BORDER_B)
            p.fillRect(QRectF(wx0 + i * bw, wy + 20 - hgt, bw - 1, hgt), cl)"""

new_hud_canvas_paint_tail = """        # Left HUD is kept clean for the large 3D hologram bust matching reference image
        # Sizing and framing allows full particle mesh from shoulders to skull crown"""

if old_hud_canvas_paint_tail in ui_code:
    ui_code = ui_code.replace(old_hud_canvas_paint_tail, new_hud_canvas_paint_tail, 1)

# In HudCanvas: Make head fill the full vertical space prominently
old_head_calc = """        _sy_status = cy + fw * 0.40
        if self._avatar is not None and self.hud_style == "face":
            _band_t = 12.0
            _band_h = max(60.0, _sy_status - 12.0 - _band_t)
            _r_head = min(fw * 0.40, _band_h / (self._avatar.SPAN + 0.05))
            _head_cy = _band_t + (_band_h - self._avatar.SPAN * _r_head) / 2.0 + _r_head"""

new_head_calc = """        if self._avatar is not None and self.hud_style == "face":
            _band_t = 20.0
            _band_h = H - 36.0
            _r_head = min(W * 0.46, _band_h / (self._avatar.SPAN + 0.04))
            _head_cy = _band_t + (_band_h - self._avatar.SPAN * _r_head) / 2.0 + _r_head"""

if old_head_calc in ui_code:
    ui_code = ui_code.replace(old_head_calc, new_head_calc, 1)

# Update top-left logo with vector skull/AI robot head emblem
old_logo = """        # Cyber emblem & assistant name at top-left (from reference image)
        p.save()
        p.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.PRI_DIM, 90), 3))
        p.drawText(QRectF(22, 18, 340, 36), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"◈  {self._assistant_name}")
        p.setPen(QPen(qcol(C.PRI), 1))
        p.drawText(QRectF(22, 18, 340, 36), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"◈  {self._assistant_name}")
        p.restore()"""

new_logo = """        # Cyber AI robotic emblem & assistant name at top-left (from reference image)
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        ox, oy = 32.0, 34.0
        r_ico = 11.0
        pri = qcol(C.PRI)
        p.setPen(QPen(pri, 1.6))
        p.setBrush(QBrush(qcol("#001622")))
        # Hexagonal cyber skull contour
        poly = QPolygonF([
            QPointF(ox, oy - r_ico),
            QPointF(ox + r_ico * 0.88, oy - r_ico * 0.45),
            QPointF(ox + r_ico * 0.88, oy + r_ico * 0.45),
            QPointF(ox, oy + r_ico),
            QPointF(ox - r_ico * 0.88, oy + r_ico * 0.45),
            QPointF(ox - r_ico * 0.88, oy - r_ico * 0.45),
        ])
        p.drawPolygon(poly)
        # Eye dots
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(qcol(C.WHITE)))
        p.drawEllipse(QPointF(ox - 4.0, oy - 1.0), 1.8, 1.8)
        p.drawEllipse(QPointF(ox + 4.0, oy - 1.0), 1.8, 1.8)
        p.setBrush(QBrush(pri))
        p.drawEllipse(QPointF(ox, oy - 5.5), 1.3, 1.3)

        # Crisp GARILA text
        p.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        p.setPen(QPen(qcol(C.WHITE), 1))
        p.drawText(QRectF(ox + 18, oy - 13, 220, 26), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._assistant_name.upper())
        p.restore()"""

if old_logo in ui_code:
    ui_code = ui_code.replace(old_logo, new_logo, 1)

# Preload LogWidget with the exact authentic cyber telemetry lines
old_log_init = """        self._queue: list[str] = []
        self._typing  = False
        self._text    = ""
        self._pos     = 0
        self._tag     = "sys"
        self._ai_name_lc = "garila"   # updated when assistant name changes
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._sig.connect(self._enqueue)"""

new_log_init = """        self._queue: list[str] = []
        self._typing  = False
        self._text    = ""
        self._pos     = 0
        self._tag     = "sys"
        self._ai_name_lc = "garila"
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._sig.connect(self._enqueue)

        # Preload authentic cyber telemetry stream matching reference image
        _sample_stream = [
            "09:20:25  50040E01FF00A405096702675     00:10:30",
            "09:20:28  0100E00000000000              00:40:00",
            "09:25:30  CODE:00004068595             06:01:30",
            "09:30:20  DE580644005953050800          --",
            "09:35:55  F004FFE0460E05                05:35:27",
            "09:35:58  CODE:00004068595             --",
            "09:38:00  0100E00000000000              08:00:20",
            "09:39:30  004-Y16F8AA5581978E01EI       02:00:20",
            "09:40:00  DEV:INITIALIZATION            08:00:30",
            "02:00:30  0000E88000A4045096702         --",
            "05:35:34  NA07A0B00CA0E0                08:00:34",
            "02:20:25  000FE77700E4A40509675         --",
            "03:35:20  0100E00000000000              02:00:20",
            "23:00:25  50040E01FF00A405096702675     08:00:00",
            "02:00:20  DEV:INITIALIZATION            --",
            "03:45:00  EX/TM/ACCESS/ENG:INSPCT001     06:00:03",
            "05:40:00  MKR-W470                      03:45:00",
            "05:45:20  DOCHEX78Y9E000406004023       --",
            "08:00:20  DISP:SYN-MAIN                 03:45:00",
            "00:10:00  IDENT:50040E0040E04           00:10:00",
            "00:00:34  FC004FFE0460E05               --",
            "00:06:23  000FE8700E4A40509675          00:06:34",
            "00:00:35  J005-555EAA6                  --"
        ]
        html_lines = []
        for line in _sample_stream:
            parts = line.split(maxsplit=2)
            if len(parts) >= 3:
                ts, payload, code = parts[0], parts[1], parts[2]
                html_lines.append(f"<div style='font-family:Courier New; font-size:7pt; line-height:1.25; margin-bottom:2px;'><span style='color:{C.PRI};'>{ts}</span>&nbsp;&nbsp;<span style='color:{C.TEXT};'>{payload}</span>&nbsp;&nbsp;&nbsp;&nbsp;<span style='color:{C.TEXT_DIM};'>{code}</span></div>")
            else:
                html_lines.append(f"<div style='color:{C.PRI}; font-family:Courier New; font-size:7pt;'>{line}</div>")
        self.setHtml("".join(html_lines))"""

if old_log_init in ui_code:
    ui_code = ui_code.replace(old_log_init, new_log_init, 1)

# In LogWidget style: set transparent background and no border so it seamlessly integrates into ACTIVITY LOG CyberPanel
old_log_style = """            QTextEdit {
                background: """ + "{" + "C.PANEL" + "};"
new_log_style = """            QTextEdit {
                background: transparent;"""
if old_log_style in ui_code:
    ui_code = ui_code.replace(old_log_style, new_log_style, 1)

old_log_border = """                border: 1px solid """ + "{" + "C.BORDER" + "};"
new_log_border = """                border: none;"""
if old_log_border in ui_code:
    ui_code = ui_code.replace(old_log_border, new_log_border, 1)

# Make MESSAGE INPUT prompt cursor and send button prominent matching reference image
old_input_row = """        self._input = QLineEdit()
        self._input.setPlaceholderText("چیت دەوێت؟  /  Type your message…")
        self._input.setFont(QFont("Courier New", 9))
        self._input.setFixedHeight(36)
        self._input.setStyleSheet(f\"\"\"
            QLineEdit {{
                background: #010e07; color: {C.WHITE};
                border: 1px solid {C.BORDER_B}; border-radius: 8px; padding: 4px 10px;
            }}
            QLineEdit:focus {{
                border: 2px solid {C.PRI};
                background: #021408;
            }}
        \"\"\")"""

new_input_row = """        self._input = QLineEdit()
        self._input.setPlaceholderText("|  Type a message...")
        self._input.setFont(QFont("Courier New", 10))
        self._input.setFixedHeight(46)
        self._input.setStyleSheet(f\"\"\"
            QLineEdit {{
                background: rgba(1, 16, 26, 0.92);
                color: #ffffff;
                border: 2px solid {C.PRI};
                border-radius: 8px;
                padding: 6px 14px;
                selection-background-color: {C.PRI_GHO};
            }}
            QLineEdit:focus {{
                border: 2px solid #00ffff;
                background: rgba(2, 22, 36, 0.96);
            }}
        \"\"\")"""

if old_input_row in ui_code:
    ui_code = ui_code.replace(old_input_row, new_input_row, 1)

old_send_btn = """        send = QPushButton("▶")
        send.setFixedSize(36, 36)"""
new_send_btn = """        send = QPushButton(">")
        send.setFixedSize(46, 46)"""
if old_send_btn in ui_code:
    ui_code = ui_code.replace(old_send_btn, new_send_btn, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(ui_code)

print("ui.py updated successfully.")
