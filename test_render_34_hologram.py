import numpy as np
import math
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QPolygonF, QRadialGradient, QFont
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF
import sys, time

from core.avatar_mesh import get_head_mesh

app = QApplication(sys.argv)
mesh = get_head_mesh()
base_v = mesh["verts"]
base_f = mesh["faces"]
base_n = mesh["normals"]
base_fade = mesh["fade"]

# Subdivide: compute edge midpoints
edge_to_mid = {}
new_verts = list(base_v)
new_normals = list(base_n)
new_fade = list(base_fade)

def get_mid_idx(i1, i2):
    edge = tuple(sorted((i1, i2)))
    if edge in edge_to_mid:
        return edge_to_mid[edge]
    mid_v = (base_v[i1] + base_v[i2]) * 0.5
    mid_n = (base_n[i1] + base_n[i2]) * 0.5
    norm_len = np.linalg.norm(mid_n)
    if norm_len > 1e-6:
        mid_n /= norm_len
    mid_fade = (base_fade[i1] + base_fade[i2]) * 0.5
    idx = len(new_verts)
    new_verts.append(mid_v)
    new_normals.append(mid_n)
    new_fade.append(mid_fade)
    edge_to_mid[edge] = idx
    return idx

sub_faces = []
for f in base_f:
    a, b, c = f[0], f[1], f[2]
    m_ab = get_mid_idx(a, b)
    m_bc = get_mid_idx(b, c)
    m_ca = get_mid_idx(c, a)
    sub_faces.append([a, m_ab, m_ca])
    sub_faces.append([b, m_bc, m_ab])
    sub_faces.append([c, m_ca, m_bc])
    sub_faces.append([m_ab, m_bc, m_ca])

sub_v = np.array(new_verts, dtype=np.float32)
sub_n = np.array(new_normals, dtype=np.float32)
sub_f = np.array(sub_faces, dtype=np.int32)
sub_fade = np.array(new_fade, dtype=np.float32)

# Unique edges for micro-wireframe
all_edges = np.vstack([sub_f[:, [0, 1]], sub_f[:, [1, 2]], sub_f[:, [2, 0]]])
all_edges = np.sort(all_edges, axis=1)
unique_edges = np.unique(all_edges, axis=0)

print(f"Subdivided mesh: {len(sub_v)} verts, {len(sub_f)} faces, {len(unique_edges)} edges")

# Render offscreen test
W, H = 800, 900
px = QPixmap(W, H)
px.fill(QColor("#000000"))
p = QPainter(px)
p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

# Posed at 3/4 profile angle
yaw = 0.62    # ~36 degrees to the right (matching reference image)
pitch = -0.09 # slight downward tilt
roll = 0.03

cy, sy = math.cos(yaw), math.sin(yaw)
cp, sp = math.cos(pitch), math.sin(pitch)
cr, sr = math.cos(roll), math.sin(roll)

# Rotation matrix
R_yaw = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
R_pitch = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)
R_roll = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], dtype=np.float32)
R = R_roll @ R_pitch @ R_yaw

posed_v = sub_v @ R.T
posed_n = sub_n @ R.T

# Camera projection
_CAM_D = 4.8
cx, cy_pos = W * 0.48, H * 0.52
r = 280.0

w_depth = _CAM_D - posed_v[:, 2]
np.maximum(w_depth, 0.35, out=w_depth)
k = (_CAM_D / w_depth) * r
xs = cx + posed_v[:, 0] * k
ys = cy_pos - posed_v[:, 1] * k
nz = posed_n[:, 2]

# 1. Multi-tier radiant cyan aura behind head
ar = r * 2.0
grad = QRadialGradient(cx, cy_pos - 40, ar)
grad.setColorAt(0.00, QColor(0, 240, 255, 90))
grad.setColorAt(0.30, QColor(0, 180, 255, 45))
grad.setColorAt(0.65, QColor(0, 90, 180, 15))
grad.setColorAt(1.00, QColor(0, 0, 0, 0))
p.setPen(Qt.PenStyle.NoPen)
p.setBrush(QBrush(grad))
p.drawEllipse(QRectF(cx - ar, cy_pos - 40 - ar, ar * 2, ar * 2))

# 2. Dense swirling galaxy / orbital particle bands (450 particles)
np.random.seed(42)
n_particles = 450
orbit_theta = np.linspace(0, 8 * np.pi, n_particles)
orbit_r = 1.1 + 0.95 * (orbit_theta / (8 * np.pi)) + np.random.normal(0, 0.08, n_particles)
orbit_y = np.linspace(-1.4, 1.2, n_particles) + np.sin(orbit_theta * 1.5) * 0.25
orbit_x = orbit_r * np.cos(orbit_theta + 0.8)
orbit_z = orbit_r * np.sin(orbit_theta + 0.8)

orb_pts = np.stack([orbit_x, orbit_y, orbit_z], axis=1).astype(np.float32)
orb_posed = orb_pts @ R.T
orb_w = _CAM_D - orb_posed[:, 2]
np.maximum(orb_w, 0.35, out=orb_w)
orb_k = (_CAM_D / orb_w) * r
orb_xs = cx + orb_posed[:, 0] * orb_k
orb_ys = cy_pos - orb_posed[:, 1] * orb_k

# Draw back particles (z < 0)
for ox, oy, oz in zip(orb_xs, orb_ys, orb_posed[:, 2]):
    if oz < 0:
        p.setBrush(QBrush(QColor(0, 200, 255, int(max(20, min(180, 120 + oz * 40))))))
        p.drawEllipse(QPointF(float(ox), float(oy)), 1.6, 1.6)

# 3. Translucent Volumetric Depth Fill
fn = np.cross(posed_v[sub_f[:, 1]] - posed_v[sub_f[:, 0]], posed_v[sub_f[:, 2]] - posed_v[sub_f[:, 0]])
fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-9)
face_nz = fn[:, 2]
vis_f = np.flatnonzero(face_nz > 0.02)

fres_f = np.clip(1.0 - face_nz[vis_f], 0.0, 1.0) ** 1.6
shade_al = np.clip((12.0 + 36.0 * fres_f), 0, 75).astype(np.int32)

p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
for f_idx, al in zip(vis_f, shade_al):
    if al < 6: continue
    pts = [QPointF(float(xs[i]), float(ys[i])) for i in sub_f[f_idx]]
    p.setBrush(QBrush(QColor(0, 180, 255, int(al))))
    p.drawPolygon(QPolygonF(pts))
p.setRenderHint(QPainter.RenderHint.Antialiasing, True)

# 4. Luminous Micro-Wireframe
e0, e1 = unique_edges[:, 0], unique_edges[:, 1]
edge_nz = 0.5 * (nz[e0] + nz[e1])
edge_fade = 0.5 * (sub_fade[e0] + sub_fade[e1])
front_edges = np.flatnonzero(edge_nz > -0.15)

for idx in front_edges:
    i0, i1 = e0[idx], e1[idx]
    al = int(np.clip((35 + 180 * max(0.0, edge_nz[idx])) * edge_fade[idx], 15, 230))
    p.setPen(QPen(QColor(0, 240, 255, al), 1.0))
    p.drawLine(QPointF(float(xs[i0]), float(ys[i0])), QPointF(float(xs[i1]), float(ys[i1])))

# 5. High-Density Particle Nodes (3,900+ points)
front_v = np.flatnonzero(nz > -0.10)
for idx in front_v:
    fade = sub_fade[idx]
    al = int(np.clip((70 + 170 * max(0.0, nz[idx])) * fade, 20, 255))
    fx, fy = float(xs[idx]), float(ys[idx])
    # Cyan bloom halo
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QBrush(QColor(0, 240, 255, int(al * 0.4))))
    p.drawEllipse(QPointF(fx, fy), 2.4, 2.4)
    # Bright inner white-cyan core
    p.setBrush(QBrush(QColor(220, 250, 255, al)))
    p.drawEllipse(QPointF(fx, fy), 1.1, 1.1)

# 6. Branching Lightning / Synaptic Circuit Veins
# Construct branching tree across visible 3/4 profile
synapse_trees = [
    # Temple to cheek and jaw
    [21, 54, 103, 67, 109, 10, 151, 9, 8, 168, 6, 197, 195, 5, 4, 1, 19, 94, 2],
    # Forehead down left temple over ear to neck
    [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400],
    # Cheektree
    [109, 67, 103, 54, 21, 162, 127, 234, 93, 132, 58, 172, 136, 150, 149, 176],
    # Neck down to left clavicle & shoulder
    [176, 58, 132, 149, 150, 136, 172, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
]

for s_path in synapse_trees:
    valid_pts = [QPointF(float(xs[i]), float(ys[i])) for i in s_path if i < len(xs)]
    if len(valid_pts) > 1:
        # Outer deep cyan glow
        p.setPen(QPen(QColor(0, 180, 255, 160), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPolyline(valid_pts)
        # Inner brilliant neon cyan
        p.setPen(QPen(QColor(0, 240, 255, 230), 2.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPolyline(valid_pts)
        # Core electric white lightning
        p.setPen(QPen(QColor(255, 255, 255, 255), 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawPolyline(valid_pts)
        # Electric sparks
        for spark_i in [len(valid_pts)//3, (2*len(valid_pts))//3]:
            pt = valid_pts[spark_i]
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(QColor(0, 240, 255, 160)))
            p.drawEllipse(pt, 6.0, 6.0)
            p.setBrush(QBrush(QColor(255, 255, 255, 255)))
            p.drawEllipse(pt, 2.5, 2.5)

# 7. Foreground floating galaxy particles (z >= 0)
for ox, oy, oz in zip(orb_xs, orb_ys, orb_posed[:, 2]):
    if oz >= 0:
        al = int(max(40, min(255, 140 + oz * 60)))
        sz = 2.2 + oz * 0.8
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(0, 240, 255, int(al * 0.35))))
        p.drawEllipse(QPointF(float(ox), float(oy)), float(sz * 2.2), float(sz * 2.2))
        p.setBrush(QBrush(QColor(180, 245, 255, al)))
        p.drawEllipse(QPointF(float(ox), float(oy)), float(sz), float(sz))

p.end()
out_test = r"C:\Users\ahmad\Desktop\Mark-LIV-main\test_34_hologram.png"
px.save(out_test)
print("Saved 3/4 profile hologram test to:", out_test)
