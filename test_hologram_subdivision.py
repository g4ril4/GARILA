import numpy as np
import math
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QPixmap, QColor, QPen, QBrush, QPolygonF, QRadialGradient
from PyQt6.QtCore import Qt, QPointF, QRectF
import sys

from core.avatar_mesh import get_head_mesh

app = QApplication(sys.argv)
mesh = get_head_mesh()
base_v = mesh["verts"]
base_f = mesh["faces"]
base_n = mesh["normals"]
base_fade = mesh["fade"]

print(f"Base mesh: {len(base_v)} verts, {len(base_f)} faces")

# Subdivide: compute edge midpoints and new triangles
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

print(f"Subdivided mesh: {len(sub_v)} verts, {len(sub_f)} faces")
