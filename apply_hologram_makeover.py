import json
import re

# ── 1. Update config/api_keys.json ───────────────────────────────────────────
try:
    with open('config/api_keys.json', 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    cfg['ui_color'] = '#00F0FF'
    with open('config/api_keys.json', 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=4)
    print("config/api_keys.json ui_color updated to #00F0FF.")
except Exception as e:
    print("Could not update config/api_keys.json:", e)

# ── 2. Update core/avatar_mesh.py ─────────────────────────────────────────────
with open('core/avatar_mesh.py', 'r', encoding='utf-8') as f:
    mesh_code = f.read()

# Change wire stride to 1 to keep full high-density lattice
mesh_code = mesh_code.replace('_WIRE_STRIDE = 3', '_WIRE_STRIDE = 1', 1)

# Update _add_neck to build full clavicle, neck & wide shoulder bust
old_add_neck = '''def _add_neck(verts: np.ndarray, faces: np.ndarray):
    """A tapering tube dropped from inside the jaw; it fades out, so no shoulders."""
    ph = np.linspace(0.0, 2.0 * np.pi, _NECK_SEGS, endpoint=False)
    # Short, and flaring hard at the bottom: a straight vertical tube reads as
    # a pedestal, whereas a neck that widens into the top of the shoulders
    # reads as a bust — and the shorter it is, the larger the head can be drawn
    # in the same HUD band.
    ys = np.linspace(-5.5, -13.0, _NECK_RINGS)
    d = (ys + 5.5) / -7.5

    rx = 4.6 * (1.0 + 0.52 * d ** 1.9)
    rz = 4.1 * (1.0 + 0.38 * d ** 1.9)
    nx = rx[:, None] * np.cos(ph)[None, :]
    nz = _NECK_Z + rz[:, None] * np.sin(ph)[None, :]
    ny = ys[:, None] * np.ones_like(ph)[None, :]

    nv = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1)
    base = len(verts)
    idx = base + np.arange(_NECK_RINGS * _NECK_SEGS).reshape(_NECK_RINGS, _NECK_SEGS)

    nf = []
    for i in range(_NECK_RINGS - 1):
        for j in range(_NECK_SEGS):
            a, b = idx[i, j], idx[i, (j + 1) % _NECK_SEGS]
            c, e = idx[i + 1, (j + 1) % _NECK_SEGS], idx[i + 1, j]
            nf.append([a, b, c])
            nf.append([a, c, e])

    # Enough rings that the fade steps stay small. Each quad splits into one
    # triangle with two top vertices and one with two bottom vertices, so a
    # steep per-vertex fade gradient makes the pair land on visibly different
    # brightnesses and the neck grows a sawtooth edge.
    fade = np.ones(base)
    nd = np.repeat(d, _NECK_SEGS)
    fade = np.concatenate([fade, 1.0 - 0.72 * np.clip(nd, 0.0, 1.0) ** 1.5])
    return np.vstack([verts, nv]), np.vstack([faces, np.array(nf)]), fade'''

new_add_neck = '''def _add_neck(verts: np.ndarray, faces: np.ndarray):
    """Flaring neck and shoulder bust that extends down to collarbone and shoulders."""
    _N_RINGS, _N_SEGS = 16, 20
    ph = np.linspace(0.0, 2.0 * np.pi, _N_SEGS, endpoint=False)
    ys = np.linspace(-5.0, -19.5, _N_RINGS)
    d = (ys + 5.0) / -14.5  # 0.0 at jaw to 1.0 at shoulders

    # Flare out horizontally (rx) for wide human shoulders and chest
    # At top (jaw/neck): rx ~ 4.8. At bottom (shoulders): rx ~ 14.6!
    rx = 4.8 * (1.0 + 2.05 * (d ** 1.6))
    # Depth (rz): front-to-back chest/back thickness
    rz = 4.2 * (1.0 + 0.85 * (d ** 1.8))

    nx = rx[:, None] * np.cos(ph)[None, :]
    nz = (_NECK_Z - 0.8 * d[:, None]) + rz[:, None] * np.sin(ph)[None, :]
    ny = ys[:, None] * np.ones_like(ph)[None, :]

    nv = np.stack([nx.ravel(), ny.ravel(), nz.ravel()], axis=1)
    base = len(verts)
    idx = base + np.arange(_N_RINGS * _N_SEGS).reshape(_N_RINGS, _N_SEGS)

    nf = []
    for i in range(_N_RINGS - 1):
        for j in range(_N_SEGS):
            a, b = idx[i, j], idx[i, (j + 1) % _N_SEGS]
            c, e = idx[i + 1, (j + 1) % _N_SEGS], idx[i + 1, j]
            nf.append([a, b, c])
            nf.append([a, c, e])

    fade = np.ones(base)
    nd = np.repeat(d, _N_SEGS)
    fade = np.concatenate([fade, np.clip(1.0 - 0.55 * (nd ** 1.4), 0.20, 1.0)])
    return np.vstack([verts, nv]), np.vstack([faces, np.array(nf)]), fade'''

assert old_add_neck in mesh_code, "old_add_neck not found"
mesh_code = mesh_code.replace(old_add_neck, new_add_neck, 1)

with open('core/avatar_mesh.py', 'w', encoding='utf-8') as f:
    f.write(mesh_code)
print("core/avatar_mesh.py updated successfully.")

# ── 3. Update ui.py palette ───────────────────────────────────────────────────
with open('ui.py', 'r', encoding='utf-8') as f:
    ui_code = f.read()

old_c_class = '''class C:
    BG        = "#020a06"
    PANEL     = "#03120a"
    PANEL2    = "#04170d"
    BORDER    = "#0b3b20"
    BORDER_B  = "#145e33"
    BORDER_A  = "#0f4a28"
    PRI       = "#00ff9d"
    PRI_DIM   = "#00995e"
    PRI_GHO   = "#002617"
    ACC       = "#ffb300"
    ACC2      = "#ffd000"
    GREEN     = "#00ff9d"
    GREEN_D   = "#00aa66"
    RED       = "#ff3355"
    MUTED_C   = "#ff3366"
    TEXT      = "#a8ffd7"
    TEXT_DIM  = "#3d946d"
    TEXT_MED  = "#5ec797"
    WHITE     = "#e6fff4"
    DARK      = "#020f08"
    BAR_BG    = "#03180e"'''

new_c_class = '''class C:
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

assert old_c_class in ui_code, "old_c_class not found"
ui_code = ui_code.replace(old_c_class, new_c_class, 1)

with open('ui.py', 'w', encoding='utf-8') as f:
    f.write(ui_code)
print("ui.py palette updated to Neon Cyan.")

# ── 4. Update core/avatar.py ──────────────────────────────────────────────────
with open('core/avatar.py', 'r', encoding='utf-8') as f:
    av_code = f.read()

# Make shaded False by default for the ethereal hologram look
av_code = av_code.replace('shaded = True', 'shaded = False', 1)

# Increase orbital particles count to 260
av_code = re.sub(r'n_orbit\s*=\s*\d+', 'n_orbit = 260', av_code)
av_code = re.sub(r'self\._orbit_count\s*=\s*\d+', 'self._orbit_count = 260', av_code)

# Add _orbit_phases in __init__
old_orbit_arrays = '''        self._orbit_angles = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)
        self._orbit_radii = np.random.uniform(1.2, 2.35, n_orbit).astype(np.float32)
        self._orbit_heights = np.random.uniform(-1.25, 1.35, n_orbit).astype(np.float32)
        self._orbit_speeds = (np.random.uniform(0.35, 1.15, n_orbit) * np.random.choice([-1, 1], n_orbit)).astype(np.float32)
        self._orbit_sizes = np.random.uniform(1.3, 3.2, n_orbit).astype(np.float32)
        self._orbit_alphas = np.random.uniform(110, 230, n_orbit).astype(np.float32)'''

new_orbit_arrays = '''        self._orbit_angles = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)
        self._orbit_radii = np.random.uniform(0.9, 2.65, n_orbit).astype(np.float32)
        self._orbit_heights = np.random.uniform(-1.85, 1.45, n_orbit).astype(np.float32)
        self._orbit_speeds = (np.random.uniform(0.25, 1.05, n_orbit) * np.random.choice([-1, 1], n_orbit)).astype(np.float32)
        self._orbit_sizes = np.random.uniform(1.2, 3.8, n_orbit).astype(np.float32)
        self._orbit_alphas = np.random.uniform(90, 245, n_orbit).astype(np.float32)
        self._orbit_phases = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)'''

if old_orbit_arrays in av_code:
    av_code = av_code.replace(old_orbit_arrays, new_orbit_arrays, 1)

# Add branching synapses across face, skull, neck and shoulders
old_synapse_paths = '''        self._synapse_paths = [
            [10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2],
            [338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400],
            [109, 67, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172, 136, 150, 149, 176],
            [10, 338, 297, 332, 284, 251, 389, 264, 447, 366, 401, 435, 367, 364],
            [10, 109, 67, 103, 54, 21, 162, 34, 227, 137, 177, 215, 138, 135],
        ]'''

new_synapse_paths = '''        # Rich branching neural synaptic tree across skull, temples, cheek, jaw, neck & shoulders
        self._synapse_paths = [
            [10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 164, 0, 11, 12, 13, 14, 15, 16, 17],
            [338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 468, 469, 470, 471],
            [109, 67, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172, 136, 150, 149, 176, 472, 473, 474],
            [10, 338, 297, 332, 284, 251, 389, 264, 447, 366, 401, 435, 367, 364, 395, 369, 396, 475, 476],
            [10, 109, 67, 103, 54, 21, 162, 34, 227, 137, 177, 215, 138, 135, 169, 170, 140, 171, 477, 478],
            [284, 251, 389, 356, 454, 323, 479, 480, 481, 482, 483, 484],
            [54, 21, 162, 127, 234, 93, 485, 486, 487, 488, 489, 490],
        ]'''

if old_synapse_paths in av_code:
    av_code = av_code.replace(old_synapse_paths, new_synapse_paths, 1)

# Update paint() method in HoloAvatar to include multi-stop radiant bloom, depth fill, and floating sci-fi particle swarm
old_paint_method = '''        verts, norms = self._pose()

        # ── aura ────────────────────────────────────────────────────────────
        ar = r * 1.95
        grad = QRadialGradient(cx, cy, ar)
        grad.setColorAt(0.00, _c(primary, 34 + 66 * amp))
        grad.setColorAt(0.38, _c(primary, 20 + 40 * amp))
        grad.setColorAt(1.00, _c(primary, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QRectF(cx - ar, cy - ar, ar * 2, ar * 2))

        # ── project ─────────────────────────────────────────────────────────
        w = _CAM_D - verts[:, 2]
        np.maximum(w, 0.35, out=w)
        k = (_CAM_D / w) * r
        xs = cx + verts[:, 0] * k
        ys = cy - verts[:, 1] * k

        # Behind head: orbital cyber particles
        self._paint_orbitals(p, cx, cy, r, primary, accent, amp, front_only=False)

        if self.shaded:
            self._paint_surface(p, xs, ys, norms, verts, primary, bg, amp)

        # Neural synapses / glowing cyber veins
        self._paint_synapses(p, xs, ys, norms, primary, accent, amp)

        # Wireframe lattice
        self._paint_wire(p, xs, ys, norms, verts, primary, bg, amp)

        # Particle node network (glowing cyber vertices)
        self._paint_particle_nodes(p, xs, ys, norms, verts, primary, accent, amp)

        # Facial features (lids, brows, lips)
        self._paint_features(p, xs, ys, norms, r, primary, accent, bg, amp)

        # In front of head: orbital cyber particles
        self._paint_orbitals(p, cx, cy, r, primary, accent, amp, front_only=True)'''

new_paint_method = '''        verts, norms = self._pose()

        # ── 1. Intense Radiant Aura / Glow Bloom (Multi-tier Neon Cyan) ─────
        ar = r * 2.15
        grad = QRadialGradient(cx, cy, ar)
        grad.setColorAt(0.00, _c(primary, int(55 + 95 * amp)))
        grad.setColorAt(0.28, _c(primary, int(30 + 55 * amp)))
        grad.setColorAt(0.65, _c(primary, int(10 + 20 * amp)))
        grad.setColorAt(1.00, _c(primary, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QRectF(cx - ar, cy - ar, ar * 2, ar * 2))

        # ── 2. 3D Project ──────────────────────────────────────────────────
        w = _CAM_D - verts[:, 2]
        np.maximum(w, 0.35, out=w)
        k = (_CAM_D / w) * r
        xs = cx + verts[:, 0] * k
        ys = cy - verts[:, 1] * k

        # ── 3. Background floating digital particles ────────────────────────
        self._paint_orbitals(p, cx, cy, r, primary, accent, amp, front_only=False)

        # ── 4. Translucent Volumetric Hologram Glass (Depth without solid opacity) ─
        self._paint_holo_depth(p, xs, ys, norms, verts, primary, bg, amp)

        # ── 5. Branching electric lightning / neural synapses ──────────────
        self._paint_synapses(p, xs, ys, norms, primary, accent, amp)

        # ── 6. Luminous wireframe / circuit lattice ────────────────────────
        self._paint_wire(p, xs, ys, norms, verts, primary, bg, amp)

        # ── 7. High-density glowing particle nodes at vertices ──────────────
        self._paint_particle_nodes(p, xs, ys, norms, verts, primary, accent, amp)

        # ── 8. Facial features (luminous eye contours, radiant pupils, lips) 
        self._paint_features(p, xs, ys, norms, r, primary, accent, bg, amp)

        # ── 9. Foreground floating digital particles ────────────────────────
        self._paint_orbitals(p, cx, cy, r, primary, accent, amp, front_only=True)'''

assert old_paint_method in av_code, "old_paint_method not found"
av_code = av_code.replace(old_paint_method, new_paint_method, 1)

# Add _paint_holo_depth method to HoloAvatar
holo_depth_method = '''    def _paint_holo_depth(self, p: QPainter, xs, ys, norms, verts,
                          primary: QColor, bg: QColor, amp: float) -> None:
        """Translucent volumetric hologram fill — gives 3D mass without solid opacity."""
        a, b, c = self._fa, self._fb, self._fc
        fn = np.cross(verts[b] - verts[a], verts[c] - verts[a])
        fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-9)
        ref = norms[a] + norms[b] + norms[c]
        fn *= np.sign((fn * ref).sum(1))[:, None]
        nz = fn[:, 2]
        vis = np.flatnonzero(nz > 0.02)
        if vis.size == 0:
            return

        ax, ay = xs[a][vis], ys[a][vis]
        bx, by = xs[b][vis], ys[b][vis]
        cxx, cyy = xs[c][vis], ys[c][vis]

        fres = np.clip(1.0 - nz[vis], 0.0, 1.0) ** 1.8
        alphas = (12.0 + 34.0 * fres + 16.0 * amp).astype(np.int32)
        alphas = np.clip(alphas, 0, 75)

        fz = (verts[a, 2][vis] + verts[b, 2][vis] + verts[c, 2][vis]) * (1.0 / 3.0)
        order = np.argsort(self._fgroup[vis] * 1000.0 + fz, kind="stable")
        tris = np.stack([ax, ay, bx, by, cxx, cyy], axis=1)[order]
        shade = alphas[order]

        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        p.setPen(Qt.PenStyle.NoPen)
        pr, pg, pb = primary.red(), primary.green(), primary.blue()
        for q, al in zip(tris, shade):
            if al < 6:
                continue
            p.setBrush(QColor(pr, pg, pb, int(al)))
            p.drawPolygon(QPolygonF([QPointF(q[0], q[1]), QPointF(q[2], q[3]), QPointF(q[4], q[5])]))
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
'''

# Add _paint_holo_depth before _paint_orbitals
av_code = av_code.replace('    def _paint_orbitals(', holo_depth_method + '\n    def _paint_orbitals(', 1)

# Update _paint_orbitals to incorporate drift & phases
old_orbitals_body = '''    def _paint_orbitals(self, p: QPainter, cx: float, cy: float, r: float,
                        primary: QColor, accent: QColor, amp: float, front_only: bool = False) -> None:
        """3D rotating particle field swirling around the holographic head."""
        ox = self._orbit_radii * np.cos(self._orbit_angles)
        oy = self._orbit_heights + 0.12 * np.sin(self._t * 1.8 + self._orbit_angles)
        oz = self._orbit_radii * np.sin(self._orbit_angles)

        cy_r, sy_r = math.cos(self._yaw * 0.4), math.sin(self._yaw * 0.4)
        cp_r, sp_r = math.cos(self._pitch * 0.4), math.sin(self._pitch * 0.4)

        ox2 = ox * cy_r + oz * sy_r
        oz2 = -ox * sy_r + oz * cy_r
        oy2 = oy * cp_r - oz2 * sp_r
        oz3 = oy * sp_r + oz2 * cp_r

        mask = (oz3 >= 0.0) if front_only else (oz3 < 0.0)
        if not np.any(mask):
            return

        w = _CAM_D - oz3[mask]
        np.maximum(w, 0.4, out=w)
        k = (_CAM_D / w) * r
        pxs = cx + ox2[mask] * k
        pys = cy - oy2[mask] * k
        sizes = self._orbit_sizes[mask] * (1.0 + 0.3 * amp)
        alphas = self._orbit_alphas[mask] * (0.8 + 0.4 * amp)

        p.setPen(Qt.PenStyle.NoPen)
        for x, y, sz, a in zip(pxs, pys, sizes, alphas):
            col = QColor(primary)
            col.setAlpha(int(max(0, min(255, a))))
            p.setBrush(QBrush(col))
            p.drawEllipse(QPointF(float(x), float(y)), float(sz), float(sz))'''

new_orbitals_body = '''    def _paint_orbitals(self, p: QPainter, cx: float, cy: float, r: float,
                        primary: QColor, accent: QColor, amp: float, front_only: bool = False) -> None:
        """3D drifting & swirling digital particle cloud around head and shoulders."""
        ox = self._orbit_radii * np.cos(self._orbit_angles + self._t * self._orbit_speeds)
        oy = self._orbit_heights + 0.16 * np.sin(self._t * 1.4 + self._orbit_phases)
        oz = self._orbit_radii * np.sin(self._orbit_angles + self._t * self._orbit_speeds)

        cy_r, sy_r = math.cos(self._yaw * 0.45), math.sin(self._yaw * 0.45)
        cp_r, sp_r = math.cos(self._pitch * 0.45), math.sin(self._pitch * 0.45)

        ox2 = ox * cy_r + oz * sy_r
        oz2 = -ox * sy_r + oz * cy_r
        oy2 = oy * cp_r - oz2 * sp_r
        oz3 = oy * sp_r + oz2 * cp_r

        mask = (oz3 >= 0.0) if front_only else (oz3 < 0.0)
        if not np.any(mask):
            return

        w = _CAM_D - oz3[mask]
        np.maximum(w, 0.35, out=w)
        k = (_CAM_D / w) * r
        pxs = cx + ox2[mask] * k
        pys = cy - oy2[mask] * k
        sizes = self._orbit_sizes[mask] * (1.0 + 0.35 * amp)
        alphas = self._orbit_alphas[mask] * (0.85 + 0.45 * amp)

        pr, pg, pb = primary.red(), primary.green(), primary.blue()
        p.setPen(Qt.PenStyle.NoPen)
        for x, y, sz, a in zip(pxs, pys, sizes, alphas):
            al = int(max(0, min(255, a)))
            if al < 15:
                continue
            fx, fy = float(x), float(y)
            if front_only and sz > 2.0:
                p.setBrush(QColor(pr, pg, pb, int(al * 0.35)))
                p.drawEllipse(QPointF(fx, fy), float(sz * 2.2), float(sz * 2.2))
            p.setBrush(QColor(pr, pg, pb, al))
            p.drawEllipse(QPointF(fx, fy), float(sz), float(sz))'''

assert old_orbitals_body in av_code, "old_orbitals_body not found"
av_code = av_code.replace(old_orbitals_body, new_orbitals_body, 1)

# Update _paint_synapses to draw glowing electric lines with white core and traveling sparks
old_synapses_body = '''    def _paint_synapses(self, p: QPainter, xs, ys, norms,
                        primary: QColor, accent: QColor, amp: float) -> None:
        """Glowing electric neural pathways flowing down temples and neck."""
        p.setBrush(Qt.BrushStyle.NoBrush)
        t = self._t
        for path in self._synapse_paths:
            pts = []
            for idx in path:
                if idx < len(xs):
                    pts.append(QPointF(float(xs[idx]), float(ys[idx])))
            if len(pts) < 2:
                continue

            vein_col = QColor(primary)
            vein_col.setAlpha(int(90 + 130 * amp))
            p.setPen(QPen(vein_col, 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPolyline(pts)

            n_pts = len(pts)
            pulse_idx = int((t * 5.5) % n_pts)
            if 0 <= pulse_idx < n_pts:
                pt = pts[pulse_idx]
                glow_c = QColor(255, 255, 255, int(180 + 75 * amp))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(glow_c))
                p.drawEllipse(pt, 3.2, 3.2)
                p.setBrush(QBrush(QColor(primary.red(), primary.green(), primary.blue(), 110)))
                p.drawEllipse(pt, 6.0, 6.0)'''

new_synapses_body = '''    def _paint_synapses(self, p: QPainter, xs, ys, norms,
                        primary: QColor, accent: QColor, amp: float) -> None:
        """Glowing electric neural pathways flowing across temples, jaw, neck and shoulders."""
        p.setBrush(Qt.BrushStyle.NoBrush)
        t = self._t
        pr, pg, pb = primary.red(), primary.green(), primary.blue()

        for p_i, path in enumerate(self._synapse_paths):
            pts = []
            for idx in path:
                if idx < len(xs):
                    pts.append(QPointF(float(xs[idx]), float(ys[idx])))
            if len(pts) < 2:
                continue

            # Outer electric cyan aura line
            vein_aura = QColor(pr, pg, pb, int(120 + 120 * amp))
            p.setPen(QPen(vein_aura, 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPolyline(pts)

            # Core bright white/cyan lightning line
            core_col = QColor(220, 250, 255, int(180 + 75 * amp))
            p.setPen(QPen(core_col, 1.2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawPolyline(pts)

            # Traveling energy pulse along the branch
            n_pts = len(pts)
            pulse_idx = int((t * (6.0 + p_i * 1.2)) % n_pts)
            if 0 <= pulse_idx < n_pts:
                pt = pts[pulse_idx]
                p.setPen(Qt.PenStyle.NoPen)
                # Outer cyan energy corona
                p.setBrush(QColor(pr, pg, pb, 130))
                p.drawEllipse(pt, 6.5, 6.5)
                # Bright white electric spark
                p.setBrush(QColor(255, 255, 255, int(220 + 35 * amp)))
                p.drawEllipse(pt, 2.8, 2.8)'''

assert old_synapses_body in av_code, "old_synapses_body not found"
av_code = av_code.replace(old_synapses_body, new_synapses_body, 1)

# Update _paint_particle_nodes to paint dense glowing nodes with bloom
old_particle_nodes = '''    def _paint_particle_nodes(self, p: QPainter, xs, ys, norms, verts,
                              primary: QColor, accent: QColor, amp: float) -> None:
        """Holographic particle nodes at vertices."""
        nz = norms[:, 2]
        front = nz > -0.05
        idx = np.flatnonzero(front)
        if idx.size == 0:
            return

        idx = idx[::2]
        pxs = xs[idx]
        pys = ys[idx]
        pnz = nz[idx]
        p_fade = self._fade[idx]

        p.setPen(Qt.PenStyle.NoPen)
        scan_dist = np.abs(verts[idx, 1] - self._scan)
        scan_boost = np.exp(-(scan_dist / 0.16) ** 2)

        alphas = (80 + 140 * pnz + 80 * scan_boost + 60 * amp) * p_fade
        alphas = np.clip(alphas, 0, 255).astype(np.int32)
        sizes = 1.3 + 1.2 * pnz + 0.8 * scan_boost

        for x, y, a, sz in zip(pxs, pys, alphas, sizes):
            if a < 20:
                continue
            c = QColor(primary)
            c.setAlpha(int(a))
            p.setBrush(QBrush(c))
            p.drawEllipse(QPointF(float(x), float(y)), float(sz), float(sz))'''

new_particle_nodes = '''    def _paint_particle_nodes(self, p: QPainter, xs, ys, norms, verts,
                              primary: QColor, accent: QColor, amp: float) -> None:
        """High-density holographic particle nodes at vertices across head & shoulders."""
        nz = norms[:, 2]
        front = nz > -0.08
        idx = np.flatnonzero(front)
        if idx.size == 0:
            return

        pxs = xs[idx]
        pys = ys[idx]
        pnz = nz[idx]
        p_fade = self._fade[idx]

        p.setPen(Qt.PenStyle.NoPen)
        scan_dist = np.abs(verts[idx, 1] - self._scan)
        scan_boost = np.exp(-(scan_dist / 0.18) ** 2)

        alphas = (90 + 135 * pnz + 85 * scan_boost + 65 * amp) * p_fade
        alphas = np.clip(alphas, 0, 255).astype(np.int32)
        sizes = 1.3 + 1.2 * pnz + 0.8 * scan_boost

        pr, pg, pb = primary.red(), primary.green(), primary.blue()

        for x, y, a, sz in zip(pxs, pys, alphas, sizes):
            if a < 25:
                continue
            fx, fy = float(x), float(y)
            # Soft radial glow aura
            p.setBrush(QColor(pr, pg, pb, int(a * 0.40)))
            p.drawEllipse(QPointF(fx, fy), float(sz * 1.8), float(sz * 1.8))
            # Bright inner point
            p.setBrush(QColor(230, 250, 255, int(a)))
            p.drawEllipse(QPointF(fx, fy), float(sz * 0.75), float(sz * 0.75))'''

assert old_particle_nodes in av_code, "old_particle_nodes not found"
av_code = av_code.replace(old_particle_nodes, new_particle_nodes, 1)

# In HoloAvatar._paint_wire: enhance wireframe line brightness and glow
old_wire_body = '''    def _paint_wire(self, p: QPainter, xs, ys, norms, verts,
                    primary: QColor, bg: QColor, amp: float) -> None:
        nz = norms[:, 2]
        fres = np.abs(1.0 - np.abs(nz)) ** 1.5
        if self.shaded:
            # The lit surface underneath is opaque, so back-facing edges would
            # float on top of the face — cull them and let the wire read as
            # structure lines over skin.
            front = nz > -0.05
            va = np.where(front, 0.10 + 0.42 * fres, 0.0)
            va += 0.30 * np.exp(-((verts[:, 1] - self._scan) / 0.13) ** 2) * front
        else:
            va = np.where(nz < 0.0, 0.13 + 0.26 * fres, 0.28 + 0.72 * fres)
            va += 0.42 * np.exp(-((verts[:, 1] - self._scan) / 0.13) ** 2)
        va *= self._fade * (0.80 + 0.45 * amp)'''

new_wire_body = '''    def _paint_wire(self, p: QPainter, xs, ys, norms, verts,
                    primary: QColor, bg: QColor, amp: float) -> None:
        nz = norms[:, 2]
        fres = np.abs(1.0 - np.abs(nz)) ** 1.4
        # Ethereal translucent hologram wireframe
        va = np.where(nz < 0.0, 0.18 + 0.32 * fres, 0.38 + 0.78 * fres)
        va += 0.50 * np.exp(-((verts[:, 1] - self._scan) / 0.15) ** 2)
        va *= self._fade * (0.88 + 0.45 * amp)'''

assert old_wire_body in av_code, "old_wire_body not found"
av_code = av_code.replace(old_wire_body, new_wire_body, 1)

with open('core/avatar.py', 'w', encoding='utf-8') as f:
    f.write(av_code)
print("core/avatar.py updated successfully.")
