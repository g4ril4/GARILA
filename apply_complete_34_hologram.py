import re

with open('core/avatar.py', 'r', encoding='utf-8') as f:
    av_code = f.read()

old_init_mesh = '''        mesh = get_head_mesh()
        self._v0 = mesh["verts"]
        self._n0 = mesh["normals"]
        self._jaw = mesh["jaw"]
        self._brow_w = mesh["brow"]
        self._lips_w = mesh["lips"]
        self._lip_c = mesh["lip_centre"]
        self._fade = mesh["fade"]
        self._f = mesh["faces"]
        self._fgroup = mesh["face_group"]
        self._fa, self._fb, self._fc = (self._f[:, i] for i in range(3))
        self._e0 = mesh["edges"][:, 0]
        self._e1 = mesh["edges"][:, 1]
        self._lm = mesh["landmarks"]'''

new_init_mesh = '''        mesh = get_head_mesh()
        base_v = mesh["verts"]
        base_f = mesh["faces"]
        base_n = mesh["normals"]
        base_fade = mesh["fade"]

        # High-resolution midpoint subdivision for ultra-dense 3D holographic matrix
        edge_to_mid = {}
        new_verts = list(base_v)
        new_normals = list(base_n)
        new_fade = list(base_fade)

        def _get_mid(i1, i2):
            edge = tuple(sorted((i1, i2)))
            if edge in edge_to_mid:
                return edge_to_mid[edge]
            mv = (base_v[i1] + base_v[i2]) * 0.5
            mn = (base_n[i1] + base_n[i2]) * 0.5
            nl = np.linalg.norm(mn)
            if nl > 1e-6:
                mn /= nl
            mf = (base_fade[i1] + base_fade[i2]) * 0.5
            idx = len(new_verts)
            new_verts.append(mv)
            new_normals.append(mn)
            new_fade.append(mf)
            edge_to_mid[edge] = idx
            return idx

        sub_faces = []
        for f in base_f:
            a, b, c = f[0], f[1], f[2]
            m_ab = _get_mid(a, b)
            m_bc = _get_mid(b, c)
            m_ca = _get_mid(c, a)
            sub_faces.append([a, m_ab, m_ca])
            sub_faces.append([b, m_bc, m_ab])
            sub_faces.append([c, m_ca, m_bc])
            sub_faces.append([m_ab, m_bc, m_ca])

        self._v0 = np.array(new_verts, dtype=np.float32)
        self._n0 = np.array(new_normals, dtype=np.float32)
        self._f = np.array(sub_faces, dtype=np.int32)
        self._fade = np.array(new_fade, dtype=np.float32)

        # Precompute face indices for depth painting
        self._fa, self._fb, self._fc = (self._f[:, i] for i in range(3))

        # Unique edges across high-res subdivided lattice
        all_edges = np.vstack([self._f[:, [0, 1]], self._f[:, [1, 2]], self._f[:, [2, 0]]])
        all_edges = np.sort(all_edges, axis=1)
        uniq_e = np.unique(all_edges, axis=0)
        self._e0 = uniq_e[:, 0]
        self._e1 = uniq_e[:, 1]

        # Interpolate jaw & morph weights for new vertices
        n_orig = len(base_v)
        n_new = len(self._v0)
        self._jaw = np.zeros(n_new, dtype=np.float32)
        self._jaw[:n_orig] = mesh["jaw"]
        self._brow_w = np.zeros(n_new, dtype=np.float32)
        self._brow_w[:n_orig] = mesh["brow"]
        self._lips_w = np.zeros(n_new, dtype=np.float32)
        self._lips_w[:n_orig] = mesh["lips"]
        self._lip_c = mesh["lip_centre"]
        self._fgroup = np.zeros(len(self._f), dtype=np.float32)

        self._lm = mesh["landmarks"]'''

assert old_init_mesh in av_code, "old_init_mesh still not found"
av_code = av_code.replace(old_init_mesh, new_init_mesh, 1)

# Set base 3/4 profile pose in HoloAvatar.__init__
old_pose_vars = '''        self._yaw        = 0.26
        self._pitch      = -0.04'''
new_pose_vars = '''        self._base_yaw   = 0.62   # 3/4 Profile View (~36 degrees, matching target design)
        self._base_pitch = -0.09  # Subtle downward tilt
        self._base_roll  = 0.03
        self._yaw        = self._base_yaw
        self._pitch      = self._base_pitch
        self._roll       = self._base_roll'''
if old_pose_vars in av_code:
    av_code = av_code.replace(old_pose_vars, new_pose_vars, 1)

# Update step() to maintain 3/4 profile view permanently
old_step_sway = '''        self._yaw = 0.26 * math.sin(s * 0.31) + 0.09 * math.sin(s * 0.73 + 1.3)
        self._pitch = (0.060 * math.sin(s * 0.23 + 0.7)
                       + 0.024 * math.sin(s * 0.61))'''

new_step_sway = '''        # Subtle natural idle breathing sway anchored in 3/4 Profile View
        self._yaw = self._base_yaw + 0.035 * math.sin(s * 0.35)
        self._pitch = self._base_pitch + 0.018 * math.sin(s * 0.28)
        self._roll = self._base_roll + 0.012 * math.sin(s * 0.42)'''

assert old_step_sway in av_code, "old_step_sway not found"
av_code = av_code.replace(old_step_sway, new_step_sway, 1)

# Update _pose() to apply roll, pitch, yaw rotation matrix
old_pose_matrix = '''        cy, sy = math.cos(self._yaw), math.sin(self._yaw)
        cp, sp = math.cos(self._pitch), math.sin(self._pitch)
        m = np.array([
            [cy, 0.0, sy],
            [sp * sy, cp, -sp * cy],
            [-cp * sy, sp, cp * cy],
        ], dtype=np.float32)

        return v @ m.T, self._n0 @ m.T'''

new_pose_matrix = '''        cy, sy = math.cos(self._yaw), math.sin(self._yaw)
        cp, sp = math.cos(self._pitch), math.sin(self._pitch)
        cr, sr = math.cos(getattr(self, '_roll', 0.03)), math.sin(getattr(self, '_roll', 0.03))

        R_yaw = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], dtype=np.float32)
        R_pitch = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]], dtype=np.float32)
        R_roll = np.array([[cr, -sr, 0], [sr, cr, 0], [0, 0, 1]], dtype=np.float32)
        m = R_roll @ R_pitch @ R_yaw

        return v @ m.T, self._n0 @ m.T'''

assert old_pose_matrix in av_code, "old_pose_matrix not found"
av_code = av_code.replace(old_pose_matrix, new_pose_matrix, 1)

# Setup 450 Volumetric Galaxy & Ambient Particles in __init__
old_orbit_init_full = '''        n_orbit = 260
        self._orbit_angles = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)
        self._orbit_radii = np.random.uniform(0.9, 2.65, n_orbit).astype(np.float32)
        self._orbit_heights = np.random.uniform(-1.85, 1.45, n_orbit).astype(np.float32)
        self._orbit_speeds = (np.random.uniform(0.25, 1.05, n_orbit) * np.random.choice([-1, 1], n_orbit)).astype(np.float32)
        self._orbit_sizes = np.random.uniform(1.2, 3.8, n_orbit).astype(np.float32)
        self._orbit_alphas = np.random.uniform(90, 245, n_orbit).astype(np.float32)
        self._orbit_phases = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)'''

new_orbit_init_full = '''        # 450 Volumetric Hologram Particle Clouds & Swirling Galaxy Bands
        n_orbit = 450
        np.random.seed(42)
        theta = np.linspace(0, 8 * np.pi, n_orbit).astype(np.float32)
        radii = (1.05 + 1.15 * (theta / (8 * np.pi)) + np.random.normal(0, 0.09, n_orbit)).astype(np.float32)
        heights = (np.linspace(-1.75, 1.35, n_orbit) + np.sin(theta * 1.6) * 0.28).astype(np.float32)

        self._orbit_angles = theta
        self._orbit_radii = radii
        self._orbit_heights = heights
        self._orbit_speeds = np.random.uniform(0.35, 0.85, n_orbit).astype(np.float32)
        self._orbit_sizes = np.random.uniform(1.2, 3.2, n_orbit).astype(np.float32)
        self._orbit_alphas = np.random.uniform(110, 255, n_orbit).astype(np.float32)
        self._orbit_phases = np.random.uniform(0, 2 * math.pi, n_orbit).astype(np.float32)'''

if old_orbit_init_full in av_code:
    av_code = av_code.replace(old_orbit_init_full, new_orbit_init_full, 1)

# In _paint_features: replace green eyes with pure electric cyan & white luminous eyes
old_eyes_paint = '''                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(_c(accent, (70 + 60 * amp) * face * vis)))
                p.drawEllipse(cpt, rad, rad * vis)            # iris
                p.setBrush(QBrush(_c(accent, 245 * face * vis)))
                p.drawEllipse(cpt, rad * 0.42, rad * 0.42 * vis)   # pupil'''

new_eyes_paint = '''                p.setPen(Qt.PenStyle.NoPen)
                # Luminous Cyan Iris Ring with Glow Bloom (Zero green!)
                p.setBrush(QBrush(QColor(0, 240, 255, int(160 * face * vis))))
                p.drawEllipse(cpt, rad, rad * vis)
                # Radiant White Pupil Dot
                p.setBrush(QBrush(QColor(255, 255, 255, int(255 * face * vis))))
                p.drawEllipse(cpt, rad * 0.45, rad * 0.45 * vis)'''

if old_eyes_paint in av_code:
    av_code = av_code.replace(old_eyes_paint, new_eyes_paint, 1)

with open('core/avatar.py', 'w', encoding='utf-8') as f:
    f.write(av_code)
print("core/avatar.py successfully updated!")
