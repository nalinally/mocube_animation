import numpy as np
import pyvista as pv

# ==========================================
# voxel空間
# ==========================================

SIZE = 20
voxels = np.zeros((SIZE, SIZE, SIZE), dtype=bool)

# 初期形状 (8x8x8 = 512 voxel)
voxels[6:14, 6:14, 6:14] = True


# ==========================================
# 直方体領域の移動
# ==========================================

def move_region(grid,
                xmin, xmax,
                ymin, ymax,
                zmin, zmax,
                dx, dy, dz):

    new_grid = grid.copy()

    region = grid[
        xmin:xmax,
        ymin:ymax,
        zmin:zmax
    ].copy()

    new_grid[
        xmin:xmax,
        ymin:ymax,
        zmin:zmax
    ] = False

    nxmin = xmin + dx
    nxmax = xmax + dx

    nymin = ymin + dy
    nymax = ymax + dy

    nzmin = zmin + dz
    nzmax = zmax + dz

    new_grid[
        nxmin:nxmax,
        nymin:nymax,
        nzmin:nzmax
    ] |= region

    return new_grid


# ==========================================
# 状態列作成
# ==========================================

states = [voxels]

current = voxels

current = move_region(
    current,
    10, 14,
    6, 14,
    6, 14,
    3, 0, 0
)
states.append(current)

current = move_region(
    current,
    13, 17,
    6, 14,
    6, 14,
    0, 3, 0
)
states.append(current)

current = move_region(
    current,
    13, 17,
    9, 17,
    6, 14,
    0, 0, 3
)
states.append(current)


# ==========================================
# bool配列 → UnstructuredGrid
# ==========================================

def voxel_grid_from_bool(grid):

    image = pv.ImageData()

    image.dimensions = np.array(grid.shape) + 1
    image.spacing = (1, 1, 1)
    image.origin = (0, 0, 0)

    image.cell_data["filled"] = grid.flatten(order="F").astype(np.uint8)

    return image.threshold(
        0.5,
        scalars="filled"
    )


# ==========================================
# PyVista表示
# ==========================================

plotter = pv.Plotter()

mesh = voxel_grid_from_bool(states[0])

actor = plotter.add_mesh(
    mesh,
    show_edges=True
)

plotter.show(auto_close=False)

for state in states[1:]:

    new_mesh = voxel_grid_from_bool(state)

    plotter.remove_actor(actor)

    actor = plotter.add_mesh(
        new_mesh,
        show_edges=True
    )

    plotter.render()

    import time
    time.sleep(0.1)

plotter.show()
# plotter.interactive()