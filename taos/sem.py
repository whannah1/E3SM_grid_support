"""
taos.sem — Spectral element method primitives for np=4.

Provides GLL quadrature constants, element geometry derived from an Exodus mesh,
and SEM differential operators.  Used by taos.grid (np4 SCRIP generation) and
taos.topo (topography smoothing).

All operations assume np=4 (hard-coded throughout TAOS).
"""
import numpy as np
import netCDF4

try:
    import numba as _numba
except ImportError:
    _numba = None

#-------------------------------------------------------------------------------
# GLL quadrature constants for np=4
#
# Points are roots of (1 − ξ²) P'₃(ξ) = 0, i.e. ξ ∈ {−1, −1/√5, +1/√5, +1}.
# Weights satisfy exact integration of polynomials up to degree 2n−3 = 5.
# (Two nodes fixed at ±1 reduce the exactness by 2 vs standard Gauss-Legendre.)

_S5 = np.sqrt(5.0)

GLL_POINTS = np.array([-1.0, -1.0 / _S5, 1.0 / _S5, 1.0])

GLL_WEIGHTS = np.array([1.0 / 6.0, 5.0 / 6.0, 5.0 / 6.0, 1.0 / 6.0])


def _make_derivative_matrix(pts):
    """
    Lagrange interpolation derivative matrix for quadrature points pts.
    D[i, j] = dL_j/dξ evaluated at pts[i], where L_j is the j-th Lagrange basis.
    """
    n = len(pts)
    D = np.zeros((n, n))
    for j in range(n):
        den = np.prod([pts[j] - pts[k] for k in range(n) if k != j])
        for i in range(n):
            if i != j:
                num = np.prod([pts[i] - pts[k]
                               for k in range(n) if k != j and k != i])
                D[i, j] = num / den
            else:
                D[i, i] = sum(1.0 / (pts[i] - pts[k])
                              for k in range(n) if k != i)
    return D


GLL_DERIV = _make_derivative_matrix(GLL_POINTS)

#-------------------------------------------------------------------------------
# Exodus mesh reading


def read_exodus(path):
    """
    Read node coordinates and element connectivity from an Exodus II mesh file.

    Parameters
    ----------
    path : str or Path

    Returns
    -------
    coords : ndarray, shape (nnodes, 3)
        Node positions in 3D Cartesian.  For HOMME cube-sphere meshes these lie
        on or very near the unit sphere.
    connect : ndarray, shape (nelems, 4), dtype int
        Element connectivity as 0-indexed node indices.
    """
    with netCDF4.Dataset(str(path)) as nc:
        if 'coordx' in nc.variables:
            # split layout: separate coordx, coordy, coordz variables
            x = nc.variables['coordx'][:]
            y = nc.variables['coordy'][:]
            z = nc.variables['coordz'][:]
            xyz = np.column_stack([x, y, z])
        else:
            # packed layout: coord array of shape (ndim, nnodes)
            xyz = nc.variables['coord'][:].T
        connect = nc.variables['connect1'][:].astype(int) - 1  # 1-indexed → 0-indexed
    return xyz, connect

#-------------------------------------------------------------------------------
# Element geometry


def _bilinear_map(corner_xyz, xi_pts=None, eta_pts=None):
    """
    Compute 3D positions and reference-space partial derivatives at all points
    on a xi_pts × eta_pts grid for a batch of elements via bilinear mapping.

    Defaults to GLL_POINTS for both axes (the np=4 GLL grid).

    Corner ordering matches the standard quadrilateral convention:
      0 → (ξ=−1, η=−1),  1 → (ξ=+1, η=−1),
      2 → (ξ=+1, η=+1),  3 → (ξ=−1, η=+1)

    Parameters
    ----------
    corner_xyz : ndarray, shape (nelems, 4, 3)
        Corner positions in 3D Cartesian.
    xi_pts : ndarray, shape (m,), optional
        Reference-space ξ values.  Defaults to GLL_POINTS (length 4).
    eta_pts : ndarray, shape (n,), optional
        Reference-space η values.  Defaults to GLL_POINTS (length 4).

    Returns
    -------
    X : ndarray, shape (nelems, m, n, 3)
        3D position (before sphere projection) at each evaluation point.
    dX_dxi : ndarray, shape (nelems, m, n, 3)
    dX_deta : ndarray, shape (nelems, m, n, 3)
    """
    if xi_pts is None:
        xi_pts = GLL_POINTS
    if eta_pts is None:
        eta_pts = GLL_POINTS
    XI, ETA = np.meshgrid(xi_pts, eta_pts, indexing='ij')

    # Shape (4_corners, 4_xi, 4_eta)
    N = np.array([
        (1 - XI) * (1 - ETA) / 4,
        (1 + XI) * (1 - ETA) / 4,
        (1 + XI) * (1 + ETA) / 4,
        (1 - XI) * (1 + ETA) / 4,
    ])
    dN_dxi = np.array([
        -(1 - ETA) / 4,
         (1 - ETA) / 4,
         (1 + ETA) / 4,
        -(1 + ETA) / 4,
    ])
    dN_deta = np.array([
        -(1 - XI) / 4,
        -(1 + XI) / 4,
         (1 + XI) / 4,
         (1 - XI) / 4,
    ])

    # corner_xyz[e,c,d] × N[c,i,j] summed over c → result[e,i,j,d]
    X       = np.einsum('cij,ecd->eijd', N,       corner_xyz)
    dX_dxi  = np.einsum('cij,ecd->eijd', dN_dxi,  corner_xyz)
    dX_deta = np.einsum('cij,ecd->eijd', dN_deta, corner_xyz)
    return X, dX_dxi, dX_deta


def element_metric(coords, connect):
    """
    Compute SEM metric quantities at all np=4 GLL points for all elements.

    The element corners are bilinearly mapped to the sphere.  At each GLL point
    the covariant metric tensor is derived from the 3D tangent vectors of the
    sphere-projected mapping.

    Parameters
    ----------
    coords : ndarray, shape (nnodes, 3)
        Node positions in 3D Cartesian on the unit sphere.
    connect : ndarray, shape (nelems, 4), dtype int
        Element connectivity, 0-indexed.

    Returns
    -------
    g_det : ndarray, shape (nelems, 4, 4)
        Area element √(det g_ab) at each GLL point.
    g_contra : ndarray, shape (nelems, 4, 4, 2, 2)
        Contravariant metric g^{ab} scaled by g_det — the tensor G = g·J⁻¹(J⁻¹)ᵀ
        used in the SEM weak Laplacian for tensor hyperviscosity.
    """
    X, dX_dxi, dX_deta = _bilinear_map(coords[connect])

    r     = np.linalg.norm(X, axis=-1, keepdims=True)   # (nelems, 4, 4, 1)
    X_hat = X / r

    # Tangent vectors of the sphere-projected mapping via chain rule through x/|x|
    def _tangent(dX):
        return (dX - X_hat * np.sum(X_hat * dX, axis=-1, keepdims=True)) / r

    T1 = _tangent(dX_dxi)
    T2 = _tangent(dX_deta)

    # Covariant metric components
    g11 = np.sum(T1 * T1, axis=-1)
    g12 = np.sum(T1 * T2, axis=-1)
    g22 = np.sum(T2 * T2, axis=-1)

    det   = g11 * g22 - g12 ** 2
    g_det = np.sqrt(np.maximum(det, 0.0))

    # G^{ab} = g_det · g^{−1}_{ab} = [[g22, −g12], [−g12, g11]] / g_det
    inv_gdet = np.where(g_det > 0, 1.0 / np.where(g_det > 0, g_det, 1.0), 0.0)
    g_contra = np.empty(g11.shape + (2, 2))
    g_contra[..., 0, 0] =  g22 * inv_gdet
    g_contra[..., 0, 1] = -g12 * inv_gdet
    g_contra[..., 1, 0] = -g12 * inv_gdet
    g_contra[..., 1, 1] =  g11 * inv_gdet

    return g_det, g_contra


def gll_positions(coords, connect):
    """
    Compute longitude and latitude of all np=4 GLL points for all elements.

    Parameters
    ----------
    coords : ndarray, shape (nnodes, 3)
    connect : ndarray, shape (nelems, 4), dtype int

    Returns
    -------
    lon : ndarray, shape (nelems, 4, 4)
        Longitude in degrees, range [0, 360).
    lat : ndarray, shape (nelems, 4, 4)
        Latitude in degrees, range [−90, 90].
    """
    X, _, _ = _bilinear_map(coords[connect])
    X_hat = X / np.linalg.norm(X, axis=-1, keepdims=True)

    lon = np.degrees(np.arctan2(X_hat[..., 1], X_hat[..., 0])) % 360.0
    lat = np.degrees(np.arcsin(np.clip(X_hat[..., 2], -1.0, 1.0)))
    return lon, lat

#-------------------------------------------------------------------------------
# Unique GLL node assembly


def cv_reference_edges():
    """
    Return the 5 CV edge positions in [-1, 1] for np=4.

    These bound the 4 control volumes along each reference-space axis.
    The first and last values are the element boundaries (±1); the interior
    values are cumulative sums of GLL weights starting from -1, matching the
    homme_tool convention (surfaces_mod.F90: cv_pts(i) = cv_pts(i-1) + w(i)).
    This guarantees that the CV area for node i is exactly w[i] in reference
    space.
    """
    cv = np.empty(5)
    cv[0] = -1.0
    for i in range(4):
        cv[i + 1] = cv[i] + GLL_WEIGHTS[i]
    cv[4] = 1.0
    return cv


def unique_gll_nodes(coords, connect):
    """
    Identify unique GLL nodes across all elements.

    GLL points on shared element edges and corners appear in multiple elements
    with identical 3D Cartesian coordinates.  This function deduplicates them
    and returns the mapping needed to assemble per-node quantities.

    Parameters
    ----------
    coords : ndarray, shape (nnodes, 3)
    connect : ndarray, shape (nelems, 4), dtype int

    Returns
    -------
    unique_xyz : ndarray, shape (ncol, 3)
        Unique GLL node positions on the unit sphere.
    inverse_idx : ndarray, shape (nelems*16,)
        For each flattened (element, i, j) index, its unique node index.
        Ordering: flat_idx = elem*16 + i*4 + j.
    primary_eij : ndarray, shape (ncol, 3), dtype int
        For each unique node, the (elem, i, j) of its first occurrence in the
        flattened ordering.  Used to pick element-local data for that node.
    """
    X, _, _ = _bilinear_map(coords[connect])
    X_hat = X / np.linalg.norm(X, axis=-1, keepdims=True)   # (nelems, 4, 4, 3)
    nelems = X_hat.shape[0]

    # homme_tool visits GLL points η-major (j outer, i inner) within each
    # element: south→north rows, west→east within each row.  Transpose i↔j
    # before flattening so np.unique sees points in the same j-major order,
    # giving a node numbering that matches homme_tool's output.
    X_hat_jmaj = X_hat.transpose(0, 2, 1, 3).reshape(-1, 3)  # (nelems*16, 3)

    _, first_jidx_sorted, inverse_jidx_sorted = np.unique(
        np.round(X_hat_jmaj, decimals=10), axis=0,
        return_index=True, return_inverse=True,
    )

    # Re-order unique nodes by first appearance in the j-major traversal.
    fo_order  = np.argsort(first_jidx_sorted)
    inv_order = np.empty_like(fo_order)
    inv_order[fo_order] = np.arange(len(fo_order))

    first_jidx = first_jidx_sorted[fo_order]   # j-major flat idx of each unique node

    # Build inverse_idx in i-major convention (flat_idx = e*16 + i*4 + j) so
    # that gll_node_areas, which reshapes g_det in i-major C order, can use it
    # directly.  Convert each i-major index to its j-major equivalent before
    # looking up the unique node id.
    f_i = np.arange(nelems * 16)
    e_  = f_i // 16
    i_  = (f_i % 16) // 4
    j_  = f_i % 4
    f_j = e_ * 16 + j_ * 4 + i_               # i-major → j-major

    inverse_idx = inv_order[inverse_jidx_sorted[f_j]]

    # Decode primary (elem, i, j) from j-major flat index:
    # f_j = e*16 + j*4 + i  →  e = f//16,  j = (f%16)//4,  i = f%4
    e_prim = first_jidx // 16
    j_prim = (first_jidx % 16) // 4
    i_prim = first_jidx % 4

    unique_xyz  = X_hat_jmaj[first_jidx]
    primary_eij = np.column_stack([e_prim, i_prim, j_prim])  # [elem, ξ-idx, η-idx]

    return unique_xyz, inverse_idx, primary_eij


def gll_node_areas(g_det, inverse_idx, ncol):
    """
    Compute the mass-matrix diagonal: area of each unique GLL node's CV.

    Each element's contribution at GLL point (i, j) is w_i * w_j * g_det[e,i,j].
    Shared nodes accumulate contributions from all elements that contain them.

    Parameters
    ----------
    g_det : ndarray, shape (nelems, 4, 4)
    inverse_idx : ndarray, shape (nelems*16,)
        From unique_gll_nodes.
    ncol : int
        Number of unique nodes.

    Returns
    -------
    area : ndarray, shape (ncol,)
        Control volume areas in steradians.
    """
    WW = GLL_WEIGHTS[:, np.newaxis] * GLL_WEIGHTS[np.newaxis, :]  # (4, 4)
    contrib = (g_det * WW[np.newaxis, :, :]).reshape(-1)
    area = np.zeros(ncol)
    np.add.at(area, inverse_idx, contrib)
    return area


def cv_corner_positions(coords, connect):
    """
    Compute lon/lat of the 4 CV corners for each np=4 GLL point.

    The control volume for GLL point (i, j) spans
    [cv_edges[i], cv_edges[i+1]] × [cv_edges[j], cv_edges[j+1]] in reference
    space, where cv_edges = cv_reference_edges().  The four corners are the
    sphere-projected positions at the reference-space corner points.

    For GLL points on element edges or corners (shared nodes), only the
    geometry of the primary element is used — the CV corners are approximate
    there.  Interior GLL points are exact.

    Parameters
    ----------
    coords : ndarray, shape (nnodes, 3)
    connect : ndarray, shape (nelems, 4), dtype int

    Returns
    -------
    corner_lon : ndarray, shape (nelems, 4, 4, 4)
        Longitude in degrees, range [0, 360).
        Axis ordering: (elem, gll_xi, gll_eta, corner).
        Corners in counterclockwise order: SW, SE, NE, NW.
    corner_lat : ndarray, shape (nelems, 4, 4, 4)
        Latitude in degrees, range [−90, 90].
    """
    cv = cv_reference_edges()                                   # (5,)
    X, _, _ = _bilinear_map(coords[connect], xi_pts=cv, eta_pts=cv)
    # X shape: (nelems, 5, 5, 3)
    X_hat = X / np.linalg.norm(X, axis=-1, keepdims=True)

    all_lon = np.degrees(np.arctan2(X_hat[..., 1], X_hat[..., 0])) % 360.0
    all_lat = np.degrees(np.arcsin(np.clip(X_hat[..., 2], -1.0, 1.0)))

    # For GLL point (i, j), 4 CV corners in counterclockwise order:
    # SW (cv_edges[i], cv_edges[j]), SE (cv_edges[i+1], cv_edges[j]),
    # NE (cv_edges[i+1], cv_edges[j+1]), NW (cv_edges[i], cv_edges[j+1])
    corner_lon = np.stack([
        all_lon[:, :4, :4],   # SW
        all_lon[:, 1:,  :4],  # SE
        all_lon[:, 1:,  1:],  # NE
        all_lon[:, :4,  1:],  # NW
    ], axis=-1)               # (nelems, 4, 4, 4)
    corner_lat = np.stack([
        all_lat[:, :4, :4],
        all_lat[:, 1:,  :4],
        all_lat[:, 1:,  1:],
        all_lat[:, :4,  1:],
    ], axis=-1)

    return corner_lon, corner_lat


def cv_corners_assembled(coords, connect):
    """
    Compute lon/lat of up to 8 CV corner positions for each unique np=4 GLL node.

    Unlike cv_corner_positions (which uses only the primary element per node),
    this function assembles corners from ALL elements that share a node.

    Node types and their unique corner counts:
      - Interior nodes (1 element)  : 4 unique corners, slots 4-7 repeat the last
      - Edge nodes (2 elements)     : 6 unique corners, slots 6-7 repeat the last
      - Cube-corner nodes (3 elems) : 6 unique corners, slots 6-7 repeat the last
      - Mesh-corner nodes (4 elems) : 8 unique corners, no repeats

    The corner sequence is counterclockwise (CCW) when viewed from outside the
    sphere, matching the SCRIP format convention.

    Parameters
    ----------
    coords : ndarray, shape (nnodes, 3)
    connect : ndarray, shape (nelems, 4), dtype int

    Returns
    -------
    corner_lon : ndarray, shape (ncol, 8)
        Longitude in degrees, range [0, 360).
    corner_lat : ndarray, shape (ncol, 8)
        Latitude in degrees, range [−90, 90].
    """
    unique_xyz, inverse_idx, _ = unique_gll_nodes(coords, connect)
    ncol   = len(unique_xyz)
    nelems = connect.shape[0]

    #---------------------------------------------------------------------------
    # precompute 4 CV corner unit vectors for every (elem, i, j) position
    #
    # X_hat shape: (nelems, 5, 5, 3), indexed as X_hat[e, cv_xi, cv_eta, xyz]
    cv = cv_reference_edges()
    X, _, _ = _bilinear_map(coords[connect], xi_pts=cv, eta_pts=cv)
    X_hat = X / np.linalg.norm(X, axis=-1, keepdims=True)

    # flat index: flat = e*16 + i*4 + j
    f     = np.arange(nelems * 16)
    e_all = f // 16
    i_all = (f % 16) // 4
    j_all = f % 4

    # all_corners[flat, corner, xyz]: SW/SE/NE/NW corners for every position
    all_corners = np.stack([
        X_hat[e_all, i_all,   j_all  ],  # SW
        X_hat[e_all, i_all+1, j_all  ],  # SE
        X_hat[e_all, i_all+1, j_all+1],  # NE
        X_hat[e_all, i_all,   j_all+1],  # NW
    ], axis=1)                            # (nelems*16, 4, 3)

    #---------------------------------------------------------------------------
    # group flat positions by unique node id for efficient iteration

    order    = np.argsort(inverse_idx, kind='stable')
    uid_ord  = inverse_idx[order]
    cors_ord = all_corners[order]          # (nelems*16, 4, 3), sorted by uid

    bnd = np.concatenate([[0],
                          np.where(np.diff(uid_ord) > 0)[0] + 1,
                          [len(uid_ord)]])

    #---------------------------------------------------------------------------
    # assemble 8-corner polygon for each unique node

    corner_xyz = np.empty((ncol, 8, 3))

    for uid in range(ncol):
        s, e = int(bnd[uid]), int(bnd[uid + 1])

        # raw corners from all adjacent elements: shape ((e-s)*4, 3)
        raw = cors_ord[s:e].reshape(-1, 3)

        # deduplicate: keep first occurrence of each distinct physical point
        seen   = [raw[0]]
        for c in raw[1:]:
            if all(float(np.sum((c - sc) ** 2)) > 1e-20 for sc in seen):
                seen.append(c)
        u = np.array(seen)

        # remove the GLL node itself when present (only for corner nodes whose
        # GLL position coincides with one CV corner — i,j both in {0,3})
        node = unique_xyz[uid]
        u = u[np.sum((u - node) ** 2, axis=-1) > 1e-20]

        n_u = len(u)

        # sort CCW in the tangent plane at the node using angle around node
        ref = np.array([0., 0., 1.])          # north pole as reference direction
        if abs(float(node @ ref)) > 0.99:     # near-pole fallback
            ref = np.array([1., 0., 0.])
        e1  = ref - float(node @ ref) * node
        e1 /= np.linalg.norm(e1)
        e2  = np.cross(node, e1)              # CCW when viewed from outside sphere

        proj   = u - (u @ node)[:, None] * node
        angles = np.arctan2(proj @ e2, proj @ e1)
        u      = u[np.argsort(angles)]

        # pad to 8 by repeating the last unique corner
        result          = np.empty((8, 3))
        result[:n_u]    = u
        result[n_u:]    = u[-1]
        corner_xyz[uid] = result

    corner_lon = np.degrees(np.arctan2(corner_xyz[..., 1],
                                       corner_xyz[..., 0])) % 360.0
    corner_lat = np.degrees(np.arcsin(np.clip(corner_xyz[..., 2], -1.0, 1.0)))
    return corner_lon, corner_lat

#-------------------------------------------------------------------------------
# Numba-accelerated CV corner assembly

if _numba is not None:
    @_numba.njit(cache=True)
    def _cv_corners_kernel(bnd, cors_ord, unique_xyz, corner_xyz):
        """
        JIT-compiled inner loop for cv_corners_assembled_numba.

        For each unique GLL node, collects CV corners from all adjacent elements,
        deduplicates, removes the node itself if present, sorts CCW in the local
        tangent plane, and pads to 8 corners.

        Parameters
        ----------
        bnd        : int64[ncol+1]       boundary indices into cors_ord per unique node
        cors_ord   : float64[N, 4, 3]    SW/SE/NE/NW corners for each flat GLL position,
                                         sorted by unique node id
        unique_xyz : float64[ncol, 3]    3D positions of unique GLL nodes
        corner_xyz : float64[ncol, 8, 3] output buffer, modified in-place
        """
        ncol = unique_xyz.shape[0]

        for uid in range(ncol):
            s      = bnd[uid]
            e      = bnd[uid + 1]
            n_elem = e - s       # number of adjacent GLL positions
            n_raw  = n_elem * 4  # raw corners before dedup (max 16)

            # -------------------------------------------------------------------
            # collect raw corners into a flat fixed-size buffer
            raw = np.empty((16, 3))
            for fi in range(n_elem):
                for ci in range(4):
                    for k in range(3):
                        raw[fi * 4 + ci, k] = cors_ord[s + fi, ci, k]

            # -------------------------------------------------------------------
            # deduplicate: keep first occurrence of each distinct 3D point
            seen   = np.empty((16, 3))
            n_seen = 0
            for ri in range(n_raw):
                is_dup = False
                for si in range(n_seen):
                    d = 0.0
                    for k in range(3):
                        d += (raw[ri, k] - seen[si, k]) ** 2
                    if d <= 1e-20:
                        is_dup = True
                        break
                if not is_dup:
                    for k in range(3):
                        seen[n_seen, k] = raw[ri, k]
                    n_seen += 1

            # -------------------------------------------------------------------
            # remove the GLL node itself if present
            node = unique_xyz[uid]
            u    = np.empty((16, 3))
            n_u  = 0
            for si in range(n_seen):
                d = 0.0
                for k in range(3):
                    d += (seen[si, k] - node[k]) ** 2
                if d > 1e-20:
                    for k in range(3):
                        u[n_u, k] = seen[si, k]
                    n_u += 1

            # -------------------------------------------------------------------
            # build tangent frame at node (CCW when viewed from outside sphere)
            ref0, ref1, ref2 = 0.0, 0.0, 1.0  # north-pole reference direction
            dot_nr = node[0]*ref0 + node[1]*ref1 + node[2]*ref2
            if abs(dot_nr) > 0.99:             # near-pole fallback
                ref0, ref1, ref2 = 1.0, 0.0, 0.0
                dot_nr = node[0]*ref0 + node[1]*ref1 + node[2]*ref2

            e1 = np.empty(3)
            e1[0] = ref0 - dot_nr * node[0]
            e1[1] = ref1 - dot_nr * node[1]
            e1[2] = ref2 - dot_nr * node[2]
            norm_e1 = np.sqrt(e1[0]**2 + e1[1]**2 + e1[2]**2)
            e1[0] /= norm_e1;  e1[1] /= norm_e1;  e1[2] /= norm_e1

            e2 = np.cross(node, e1)

            # -------------------------------------------------------------------
            # project each corner onto the tangent plane and compute CCW angle
            angles = np.empty(16)
            for i in range(n_u):
                dot_un = u[i,0]*node[0] + u[i,1]*node[1] + u[i,2]*node[2]
                p0 = u[i,0] - dot_un * node[0]
                p1 = u[i,1] - dot_un * node[1]
                p2 = u[i,2] - dot_un * node[2]
                angles[i] = np.arctan2(p0*e2[0] + p1*e2[1] + p2*e2[2],
                                       p0*e1[0] + p1*e1[1] + p2*e1[2])

            idx = np.argsort(angles[:n_u])

            # -------------------------------------------------------------------
            # write sorted corners to output; pad to 8 by repeating the last
            for i in range(8):
                src = idx[i] if i < n_u else idx[n_u - 1]
                for k in range(3):
                    corner_xyz[uid, i, k] = u[src, k]

else:
    _cv_corners_kernel = None


#-------------------------------------------------------------------------------
# Tensor hyperviscosity topography smoother (replaces homme_tool topo_pgn_to_smoothed)
#
# For hypervis_scaling=2 the tensor viscosity tensorVisc = rearth^4 * D * D^T,
# where D is the gnomonic metric Jacobian.  This cancels the contravariant metric
# in the weak Laplacian and the operator reduces to pure reference-space
# derivatives.  The physical-sphere nudt is rescaled to the unit sphere by
# multiplying by rearth^2.
#
# Reference: HOMME source
#   components/homme/src/share/viscosity_base.F90  (smooth_phis, laplace_sphere_wk)
#   components/homme/src/share/cube_mod.F90         (tensorVisc for hypervis_scaling=2)
#   components/homme/src/share/physical_constants.F90  (rearth0 = 6.376e6)

_REARTH = 6.376e6  # Earth radius (m), matches HOMME physical_constants.F90


def smooth_phis(phis, g_det, inverse_idx, ncol, numcycle=6, nudt=4e-16):
    """
    Apply SEM tensor hyperviscosity smoother to a field on the np4 GLL grid.

    Equivalent to homme_tool topo_pgn_to_smoothed with:
        smooth_phis_numcycle = 6
        smooth_phis_nudt     = 4e-16
        hypervis_scaling     = 2
        se_ftype             = 2
        smooth_phis_p2filt   = 0

    Parameters
    ----------
    phis       : ndarray, shape (ncol,)
        Field to smooth (e.g. PHIS in m^2 s^-2).
    g_det      : ndarray, shape (nelems, 4, 4)
        Jacobian determinant at each GLL point (from element_metric).
    inverse_idx : ndarray, shape (nelems*16,)
        Maps flat GLL index e*16 + i*4 + j to the unique node id (from
        unique_gll_nodes).
    ncol       : int
        Number of unique GLL nodes.
    numcycle   : int
        Number of smoothing iterations (HOMME default: 6).
    nudt       : float
        Physical-sphere viscosity parameter (HOMME default: 4e-16).

    Returns
    -------
    phi_smooth : ndarray, shape (ncol,)
        Smoothed field.
    """
    nudt_u = nudt * _REARTH ** 2  # rescale to unit sphere

    nelems = g_det.shape[0]
    WW    = GLL_WEIGHTS[:, np.newaxis] * GLL_WEIGHTS[np.newaxis, :]  # (4, 4)
    M_loc = WW[np.newaxis, :, :] * g_det                             # (nelems, 4, 4)
    M_asm = gll_node_areas(g_det, inverse_idx, ncol)                 # (ncol,)

    phi = phis.copy()

    for _ in range(numcycle):
        # -------------------------------------------------------------------
        # gather to element-local array and compute reference-space gradients
        phi_e = phi[inverse_idx].reshape(nelems, 4, 4)
        dxi   = GLL_DERIV @ phi_e        # (nelems, 4, 4): ∂φ/∂ξ
        deta  = phi_e @ GLL_DERIV.T      # (nelems, 4, 4): ∂φ/∂η

        # -------------------------------------------------------------------
        # element-local weak Laplacian (negative divergence of gradient)
        pstens = -(GLL_DERIV.T @ (M_loc * dxi) + (M_loc * deta) @ GLL_DERIV)

        # -------------------------------------------------------------------
        # DSS: scatter-add at shared nodes, then apply update
        # (pstens < 0 at local maxima, so += gives diffusion, matching HOMME)
        pstens_asm = np.zeros(ncol)
        np.add.at(pstens_asm, inverse_idx, pstens.reshape(-1))

        phi += nudt_u * pstens_asm / M_asm

    return phi


def cv_corners_assembled_numba(coords, connect):
    """
    Numba-accelerated equivalent of cv_corners_assembled.

    Replaces the per-node Python loop with a @numba.njit kernel using
    fixed-size local buffers.  All upstream computation (bilinear mapping,
    node deduplication, corner sorting) is identical to the pure-Python version.
    Requires numba to be installed.

    On first call the kernel is JIT-compiled and cached to __pycache__;
    subsequent calls load from cache.

    Parameters / Returns — identical to cv_corners_assembled.
    """
    if _numba is None:
        raise ImportError(
            'numba is required for cv_corners_assembled_numba; '
            'install with: pip install numba'
        )

    unique_xyz, inverse_idx, _ = unique_gll_nodes(coords, connect)
    ncol   = len(unique_xyz)
    nelems = connect.shape[0]

    cv = cv_reference_edges()
    X, _, _ = _bilinear_map(coords[connect], xi_pts=cv, eta_pts=cv)
    X_hat = X / np.linalg.norm(X, axis=-1, keepdims=True)

    f     = np.arange(nelems * 16)
    e_all = f // 16
    i_all = (f % 16) // 4
    j_all = f % 4

    all_corners = np.stack([
        X_hat[e_all, i_all,   j_all  ],  # SW
        X_hat[e_all, i_all+1, j_all  ],  # SE
        X_hat[e_all, i_all+1, j_all+1],  # NE
        X_hat[e_all, i_all,   j_all+1],  # NW
    ], axis=1)

    order    = np.argsort(inverse_idx, kind='stable')
    uid_ord  = inverse_idx[order]
    cors_ord = all_corners[order]

    bnd = np.concatenate([[0],
                          np.where(np.diff(uid_ord) > 0)[0] + 1,
                          [len(uid_ord)]]).astype(np.int64)

    corner_xyz = np.empty((ncol, 8, 3))
    _cv_corners_kernel(bnd,
                       np.ascontiguousarray(cors_ord),
                       np.ascontiguousarray(unique_xyz),
                       corner_xyz)

    corner_lon = np.degrees(np.arctan2(corner_xyz[..., 1],
                                       corner_xyz[..., 0])) % 360.0
    corner_lat = np.degrees(np.arcsin(np.clip(corner_xyz[..., 2], -1.0, 1.0)))
    return corner_lon, corner_lat
