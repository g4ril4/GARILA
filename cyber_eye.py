import math
import random
import time
import numpy as np
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QPixmap, QColor, QPen, QBrush, QFont,
    QRadialGradient, QLinearGradient, QPainterPath, QPolygonF
)
from PyQt6.QtWidgets import QWidget, QSizePolicy

class CyberEyeCanvas(QWidget):
    """
    Advanced Holographic Cybernetic AI Eye matching media_1792674303275_e4416d9f.jpg 100%:
    - Multi-bladed mechanical camera iris/aperture shutter reacting to audio.
    - Concentric data rings, rotating gear/cog ring, terminal code scripts.
    - Almond cyber eyelid particle lattice with radiating circuit traces.
    - Swirling volumetric galaxy particle rings (cyan & neon violet).
    - Radiant anamorphic light core pupil with pulsing star flare.
    """
    def __init__(self, face_path: str = "", assistant_name: str = "GARILA", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(320, 320)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._assistant_name = assistant_name
        self.muted = False
        self.speaking = False
        self.state = "INITIALISING"

        # Animation states
        self._t = 0.0
        self._step_t = time.time()
        self._amp_disp = 0.0
        self._live_amp = 0.0
        self._visemes = None
        self._vis_i = None

        # Mechanical iris aperture blade parameters
        self._n_blades = 14
        self._aperture_open = 0.35  # 0.2 (closed) to 0.75 (wide open)
        self._target_aperture = 0.35

        # Rotation angles for rotating rings
        self._gear_angle = 0.0
        self._data_ring_angle = 0.0
        self._code_ring_angle = 0.0
        self._galaxy_angle1 = 0.0
        self._galaxy_angle2 = 0.0

        # Galaxy orbital particles (360 3D particles in tilted elliptical orbits)
        np.random.seed(1337)
        self._n_orb = 360
        self._orb_theta = np.linspace(0, 10 * math.pi, self._n_orb).astype(np.float32)
        self._orb_radii = np.random.uniform(1.05, 2.35, self._n_orb).astype(np.float32)
        self._orb_z = np.random.uniform(-0.6, 0.6, self._n_orb).astype(np.float32)
        self._orb_speeds = np.random.uniform(0.3, 0.9, self._n_orb).astype(np.float32)
        self._orb_sizes = np.random.uniform(1.2, 3.2, self._n_orb).astype(np.float32)
        self._orb_types = np.random.choice([0, 1], self._n_orb, p=[0.55, 0.45])  # 0: Cyan, 1: Violet

        # Eyelid particle lattice points (240 micro-particles)
        n_eye = 120
        t_param = np.linspace(0, math.pi, n_eye)
        # Upper eyelid: (cos t, sin t)
        up_x = np.cos(t_param)
        up_y = np.sin(t_param) * 0.58
        # Lower eyelid
        dn_x = np.cos(t_param)
        dn_y = -np.sin(t_param) * 0.52
        self._eyelid_x = np.concatenate([up_x, dn_x]).astype(np.float32)
        self._eyelid_y = np.concatenate([up_y, dn_y]).astype(np.float32)

        # 60 FPS animation timer
        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(16)

    def glance(self, dx: float, dy: float, hold: float = 1.1) -> None:
        pass  # Cyber Eye is front-facing locked

    def push_visemes(self, frames, hop: float, at: float) -> None:
        try:
            if not frames: return
            self._live_amp = max(f[0] for f in frames)
        except Exception:
            pass

    def _step(self):
        now = time.time()
        dt = max(0.001, min(0.08, now - self._step_t))
        self._step_t = now
        self._t += dt

        # Audio amplitude smoothing
        self._live_amp *= 0.88
        self._amp_disp += (self._live_amp - self._amp_disp) * 0.45
        amp = self._amp_disp

        # Aperture reactivity
        if self.speaking or amp > 0.03:
            self._target_aperture = 0.32 + min(0.48, amp * 0.65)
        elif self.state in ("THINKING", "PROCESSING"):
            self._target_aperture = 0.30 + 0.15 * math.sin(self._t * 4.0)
        else:
            self._target_aperture = 0.28 + 0.04 * math.sin(self._t * 1.5)

        self._aperture_open += (self._target_aperture - self._aperture_open) * 0.22

        # Rotate tech rings
        self._gear_angle += dt * 0.35
        self._data_ring_angle -= dt * 0.50
        self._code_ring_angle += dt * 0.22
        self._galaxy_angle1 += dt * 0.45
        self._galaxy_angle2 -= dt * 0.38

        if self.isVisible():
            self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        if not p.isActive():
            return
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        W, H = self.width(), self.height()
        # Pitch black background
        p.fillRect(self.rect(), QColor("#000000"))

        cx, cy = W * 0.50, H * 0.50
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
        amp = self._amp_disp

        # ── 1. Top-Left Emblem + GARILA Logo ─────────────────────────────────
        self._paint_top_logo(p, col_violet, col_cyan, col_white)

        # ── 2. Ambient Nebula Violet/Cyan Glow (Background Bloom) ─────────────
        self._paint_nebula_glow(p, cx, cy, base_r, amp)

        # ── 3. Swirling 3D Galaxy Cosmic Rings ────────────────────────────────
        self._paint_galaxy_rings(p, cx, cy, base_r, col_cyan, col_violet, amp)

        # ── 4. Almond Cyber Eyelid Particle Lattice & Circuit Traces ──────────
        self._paint_eyelid_lattice(p, cx, cy, base_r, col_cyan, col_violet, amp)

        # ── 5. Mechanical Gear / Cog Aperture Ring ────────────────────────────
        self._paint_gear_ring(p, cx, cy, base_r, col_cyan, col_violet)

        # ── 6. Concentric Iris Array & Terminal Scripts ───────────────────────
        self._paint_iris_array(p, cx, cy, base_r, col_cyan, col_violet, amp)

        # ── 7. Multi-bladed Camera Iris / Aperture Shutter ────────────────────
        self._paint_aperture_blades(p, cx, cy, base_r, col_cyan, col_violet)

        # ── 8. Radiant Light Star Core Pupil ──────────────────────────────────
        self._paint_core_pupil(p, cx, cy, base_r, col_cyan, col_violet, col_white, amp)

        p.end()

    def _paint_top_logo(self, p: QPainter, col_violet: QColor, col_cyan: QColor, col_white: QColor):
        p.save()
        ox, oy = 32.0, 32.0
        r_ico = 11.0

        # Hexagonal cyber skull icon
        poly = QPolygonF([
            QPointF(ox, oy - r_ico),
            QPointF(ox + r_ico * 0.88, oy - r_ico * 0.45),
            QPointF(ox + r_ico * 0.88, oy + r_ico * 0.45),
            QPointF(ox, oy + r_ico),
            QPointF(ox - r_ico * 0.88, oy + r_ico * 0.45),
            QPointF(ox - r_ico * 0.88, oy - r_ico * 0.45),
        ])
        p.setPen(QPen(col_violet, 1.8))
        p.setBrush(QBrush(QColor("#100018")))
        p.drawPolygon(poly)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(col_white))
        p.drawEllipse(QPointF(ox - 3.8, oy - 1.0), 1.8, 1.8)
        p.drawEllipse(QPointF(ox + 3.8, oy - 1.0), 1.8, 1.8)
        p.setBrush(QBrush(col_cyan))
        p.drawEllipse(QPointF(ox, oy - 5.0), 1.3, 1.3)

        p.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        p.setPen(QPen(col_white, 1))
        p.drawText(QRectF(ox + 18, oy - 13, 220, 26), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self._assistant_name.upper())
        p.restore()

    def _paint_nebula_glow(self, p: QPainter, cx: float, cy: float, r: float, amp: float):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)
        glow_r = r * 1.6
        grad = QRadialGradient(cx, cy, glow_r)
        # Deep violet and cyan ambient glow
        grad.setColorAt(0.00, QColor(140, 20, 220, int(60 + 50 * amp)))
        grad.setColorAt(0.35, QColor(80, 0, 160, int(35 + 35 * amp)))
        grad.setColorAt(0.70, QColor(0, 160, 220, int(15 + 20 * amp)))
        grad.setColorAt(1.00, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(grad))
        p.drawEllipse(QRectF(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2))
        p.restore()

    def _paint_galaxy_rings(self, p: QPainter, cx: float, cy: float, r: float,
                            col_cyan: QColor, col_violet: QColor, amp: float):
        p.save()
        p.setPen(Qt.PenStyle.NoPen)

        # 1. Continuous luminous orbit tracks (tilted ellipses)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i, (rx_f, ry_f, rot, col, alpha) in enumerate([
            (1.55, 0.72, -18.0, col_violet, 90),
            (1.42, 0.65, 22.0, col_cyan, 110),
            (1.72, 0.85, -5.0, col_violet, 65),
        ]):
            p.save()
            p.translate(cx, cy)
            p.rotate(rot + math.sin(self._t * 0.8 + i) * 3.0)
            p.setPen(QPen(QColor(col.red(), col.green(), col.blue(), int(alpha + 60 * amp)), 1.2, Qt.PenStyle.DashLine))
            p.drawEllipse(QRectF(-r * rx_f, -r * ry_f, r * rx_f * 2, r * ry_f * 2))
            p.restore()

        # 2. 360 Swirling cosmic micro-particles
        pr_c, pg_c, pb_c = col_cyan.red(), col_cyan.green(), col_cyan.blue()
        pr_v, pg_v, pb_v = col_violet.red(), col_violet.green(), col_violet.blue()

        rot1 = self._galaxy_angle1
        rot2 = self._galaxy_angle2

        for i in range(self._n_orb):
            th = self._orb_theta[i] + (rot1 if self._orb_types[i] == 0 else rot2)
            rad = self._orb_radii[i] * r
            tilt = -0.32 if self._orb_types[i] == 0 else 0.38
            px = cx + rad * math.cos(th)
            py = cy + rad * math.sin(th) * 0.62 + rad * math.cos(th) * tilt * 0.45

            sz = float(self._orb_sizes[i]) * (1.0 + 0.3 * amp)
            al = int(min(255, max(30, 140 + 70 * math.sin(self._t * 3.0 + i))))

            if self._orb_types[i] == 0:
                p.setBrush(QColor(pr_c, pg_c, pb_c, al))
            else:
                p.setBrush(QColor(pr_v, pg_v, pb_v, al))
            p.drawEllipse(QPointF(px, py), sz, sz)

        p.restore()

    def _paint_eyelid_lattice(self, p: QPainter, cx: float, cy: float, r: float,
                              col_cyan: QColor, col_violet: QColor, amp: float):
        p.save()
        ew = r * 1.38
        eh = r * 0.62

        # Draw outer glowing almond contour
        path = QPainterPath()
        path.moveTo(cx - ew, cy)
        path.cubicTo(cx - ew * 0.45, cy - eh * 1.15, cx + ew * 0.45, cy - eh * 1.15, cx + ew, cy)
        path.cubicTo(cx + ew * 0.45, cy + eh * 1.05, cx - ew * 0.45, cy + eh * 1.05, cx - ew, cy)

        # Cyan outer aura
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), int(140 + 80 * amp)), 2.6))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        # Inner bright core
        p.setPen(QPen(QColor(240, 255, 255, int(200 + 55 * amp)), 1.2))
        p.drawPath(path)

        # Micro-particles along eyelid contour
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(len(self._eyelid_x)):
            px = cx + self._eyelid_x[i] * ew
            py = cy + self._eyelid_y[i] * eh
            p.setBrush(QBrush(col_cyan))
            p.drawEllipse(QPointF(float(px), float(py)), 1.6, 1.6)

        # Corner circuit traces
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 130), 1.3))
        # Left corner rays
        p.drawLine(QPointF(cx - ew, cy), QPointF(cx - ew - 35, cy - 14))
        p.drawLine(QPointF(cx - ew, cy), QPointF(cx - ew - 45, cy + 8))
        # Right corner rays
        p.drawLine(QPointF(cx + ew, cy), QPointF(cx + ew + 35, cy - 14))
        p.drawLine(QPointF(cx + ew, cy), QPointF(cx + ew + 45, cy + 8))

        p.restore()

    def _paint_gear_ring(self, p: QPainter, cx: float, cy: float, r: float,
                         col_cyan: QColor, col_violet: QColor):
        p.save()
        p.translate(cx, cy)
        p.rotate(math.degrees(self._gear_angle))

        gr = r * 0.68
        n_teeth = 22
        tooth_h = 10.0
        tooth_w_deg = 360.0 / (n_teeth * 2.2)

        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 180), 1.4))
        p.setBrush(QBrush(QColor(col_violet.red(), col_violet.green(), col_violet.blue(), 25)))

        gear_path = QPainterPath()
        for i in range(n_teeth):
            ang_deg = i * (360.0 / n_teeth)
            rad1 = math.radians(ang_deg - tooth_w_deg)
            rad2 = math.radians(ang_deg)
            rad3 = math.radians(ang_deg + tooth_w_deg)
            rad4 = math.radians(ang_deg + tooth_w_deg * 1.8)

            p1 = QPointF(gr * math.cos(rad1), gr * math.sin(rad1))
            p2 = QPointF((gr + tooth_h) * math.cos(rad2), (gr + tooth_h) * math.sin(rad2))
            p3 = QPointF((gr + tooth_h) * math.cos(rad3), (gr + tooth_h) * math.sin(rad3))
            p4 = QPointF(gr * math.cos(rad4), gr * math.sin(rad4))

            if i == 0:
                gear_path.moveTo(p1)
            else:
                gear_path.lineTo(p1)
            gear_path.lineTo(p2)
            gear_path.lineTo(p3)
            gear_path.lineTo(p4)
        gear_path.closeSubpath()
        p.drawPath(gear_path)

        p.restore()

    def _paint_iris_array(self, p: QPainter, cx: float, cy: float, r: float,
                          col_cyan: QColor, col_violet: QColor, amp: float):
        p.save()
        p.translate(cx, cy)

        # Ring 1: Calibrated dial tick marks
        dial_r = r * 0.54
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 150), 1.0))
        p.drawEllipse(QRectF(-dial_r, -dial_r, dial_r * 2, dial_r * 2))

        n_ticks = 48
        for i in range(n_ticks):
            deg = i * (360.0 / n_ticks) + math.degrees(self._data_ring_angle)
            rad = math.radians(deg)
            tick_len = 6.0 if i % 4 == 0 else 3.0
            x1 = (dial_r - tick_len) * math.cos(rad)
            y1 = (dial_r - tick_len) * math.sin(rad)
            x2 = dial_r * math.cos(rad)
            y2 = dial_r * math.sin(rad)
            p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Ring 2: Segmented pulsing arc gauges
        arc_r = r * 0.44
        p.setPen(QPen(QColor(col_violet.red(), col_violet.green(), col_violet.blue(), int(160 + 80 * amp)), 2.8))
        for span_start in (15, 105, 195, 285):
            rot_start = int((span_start + math.degrees(self._code_ring_angle)) % 360) * 16
            p.drawArc(QRectF(-arc_r, -arc_r, arc_r * 2, arc_r * 2), rot_start, 60 * 16)

        # Ring 3: Circular micro terminal scripts
        code_r = r * 0.36
        p.rotate(math.degrees(self._code_ring_angle))
        p.setFont(QFont("Courier New", 5, QFont.Weight.Bold))
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 190), 1))
        # Draw 8 radial text tags around the circle
        for idx, tag in enumerate(["GARILA//AI", "01001101", "OPTIC.V5", "10110010",
                                   "SYNAPSE", "SYS.LOCK", "01101111", "COHERENCE"]):
            p.save()
            p.rotate(idx * 45)
            p.drawText(int(code_r - 28), 3, tag)
            p.restore()

        p.restore()

    def _paint_aperture_blades(self, p: QPainter, cx: float, cy: float, r: float,
                               col_cyan: QColor, col_violet: QColor):
        p.save()
        p.translate(cx, cy)

        # Aperture outer radius & dynamic inner opening radius
        R_out = r * 0.32
        R_in = R_out * max(0.18, min(0.78, self._aperture_open))

        n = self._n_blades
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 230), 1.2))

        # Draw overlapping logarithmic camera aperture blades
        for i in range(n):
            theta = i * (2.0 * math.pi / n) + self._gear_angle * 0.4
            theta_next = (i + 1) * (2.0 * math.pi / n) + self._gear_angle * 0.4

            # Outer arc point
            x_out = R_out * math.cos(theta)
            y_out = R_out * math.sin(theta)

            # Inner tangent contact point on aperture opening circle
            tan_angle = theta + 1.15
            x_in = R_in * math.cos(tan_angle)
            y_in = R_in * math.sin(tan_angle)

            x_out2 = R_out * math.cos(theta_next)
            y_out2 = R_out * math.sin(theta_next)

            blade_poly = QPolygonF([
                QPointF(x_out, y_out),
                QPointF(x_in, y_in),
                QPointF(x_out2, y_out2),
            ])

            # Gradient blade shading (cyber metallic cyan/violet)
            grad = QLinearGradient(x_out, y_out, x_in, y_in)
            grad.setColorAt(0.0, QColor(col_violet.red(), col_violet.green(), col_violet.blue(), 160))
            grad.setColorAt(1.0, QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 210))
            p.setBrush(QBrush(grad))
            p.drawPolygon(blade_poly)

        p.restore()

    def _paint_core_pupil(self, p: QPainter, cx: float, cy: float, r: float,
                          col_cyan: QColor, col_violet: QColor, col_white: QColor, amp: float):
        p.save()
        p.translate(cx, cy)

        # Core pupil size dynamically scales with aperture opening
        core_r = (r * 0.32 * self._aperture_open) * 0.55
        core_r = max(6.0, core_r)

        # 1. Multi-pointed radiant anamorphic light star flare (8 rays)
        ray_len = core_r * (2.8 + 1.2 * amp)
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), int(160 + 80 * amp)), 1.2))
        for deg in (0, 45, 90, 135, 180, 225, 270, 315):
            rad = math.radians(deg + self._t * 15.0)
            p.drawLine(QPointF(0, 0), QPointF(ray_len * math.cos(rad), ray_len * math.sin(rad)))

        # 2. Glowing radial pupil bloom
        grad = QRadialGradient(0, 0, core_r * 2.2)
        grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        grad.setColorAt(0.35, QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 210))
        grad.setColorAt(0.70, QColor(col_violet.red(), col_violet.green(), col_violet.blue(), 110))
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QRectF(-core_r * 2.2, -core_r * 2.2, core_r * 4.4, core_r * 4.4))

        # 3. Brilliant central white star core
        p.setBrush(QBrush(col_white))
        p.drawEllipse(QPointF(0, 0), core_r * 0.55, core_r * 0.55)

        # 4. Concentric target reticle ring
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(col_cyan.red(), col_cyan.green(), col_cyan.blue(), 220), 1.0))
        p.drawEllipse(QRectF(-core_r * 0.85, -core_r * 0.85, core_r * 1.7, core_r * 1.7))

        p.restore()
