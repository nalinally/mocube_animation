####################################################
# 3次元listでvoxelの状態を管理し、pyvistaで表示する
# スレッド1: ユーザからの入力をひたすら受信してcmdsに格納
# スレッド2: cmdsに格納された入力を解釈して実行
# main()がすべての実行元なので、そこから読むと読みやすい
####################################################



import numpy as np
import pyvista as pv
import time
import threading
import sys
from func import *


MAX_STATES_NUM = 100
dt = 0.1

state = np.zeros((30, 30, 100), dtype=bool)
init_state = state
states = []
plotter = pv.Plotter()
actor = None
progress = 0
undo_cnt = 0
cmds = []
source = ""
recording = False
moves = []


# 初期化処理
def init():
    global actor
    global init_state
    state[6:14, 6:14, 6:14] = True
    init_state = state
    states.append(state)
    mesh = voxel_grid_from_bool(states[0])
    actor = plotter.add_mesh(mesh, show_edges=True)
    plotter.add_axes()
    plotter.show(auto_close=False, interactive_update=True)


# 直方体領域の移動
def move_region(grid, xmin, xmax, ymin, ymax, zmin, zmax, dx, dy, dz):
    new_grid = grid.copy()
    region = grid[xmin:xmax, ymin:ymax, zmin:zmax].copy()
    new_grid[xmin:xmax, ymin:ymax, zmin:zmax] = False
    new_grid[xmin+dx:xmax+dx, ymin+dy:ymax+dy, zmin+dz:zmax+dz] |= region
    return new_grid


# bool配列 → UnstructuredGrid
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


# PyVista表示
def show_states():
    global progress
    for state_ in states[progress:]:
        new_mesh = voxel_grid_from_bool(state_)
        actor.mapper.dataset.copy_from(new_mesh)
        plotter.render()
        if recording:
            plotter.write_frame()
        time.sleep(dt)
    progress = len(states)


# 直方体領域を1マスずつ動かしたときのt->t+1での動き
def move_step(xmin, xmax, ymin, ymax, zmin, zmax, dx, dy, dz, t):
    global state
    if t < abs(dx):
        step = 1 if dx > 0 else -1
        state = move_region(state, xmin+t*step, xmax+t*step, ymin, ymax, zmin, zmax, step, 0, 0)
    elif t < abs(dx) + abs(dy):
        step = 1 if dy > 0 else -1
        state = move_region(state, xmin+dx, xmax+dx, ymin+(t-abs(dx))*step, ymax+(t-abs(dx))*step, zmin, zmax, 0, step, 0)
    elif t < abs(dx) + abs(dy) + abs(dz):
        step = 1 if dz > 0 else -1
        state = move_region(state, xmin+dx, xmax+dx, ymin+dy, ymax+dy, zmin+(t-abs(dx)-abs(dy))*step, zmax+(t-abs(dx)-abs(dy))*step, 0, 0, step)
    else:
        return True
    return False

    
def move():
    t = 0
    finished = False
    moves_ = []
    while moves:
        moves_.append(moves.pop(0))
    while not finished:
        finished = True
        for mov in moves_:
            finished &= move_step(mov[0], mov[1], mov[2], mov[3], mov[4], mov[5], mov[6], mov[7], mov[8], t)
        states.append(state)
        t += 1
    show_states()


def set(xmin, xmax, ymin, ymax, zmin, zmax, dx, dy, dz):
    moves.append([xmin, xmax, ymin, ymax, zmin, zmax, dx, dy, dz])


# 最初の状態に戻す
def reset():
    global state
    state = init_state
    states.append(state)
    show_states()
    

# ひとつ前に戻す
def undo():
    global state
    if len(states) < 2*undo_cnt:
        return
    state = states[-2*undo_cnt]
    states.append(state)
    show_states()
    

# 数秒まつframeをつくる
def delay(duration):
    for _ in range(int(duration / dt)):
        states.append(state)
    show_states()

# コマンドを受信するだけ
def receive_cmd():
    global cmds
    while True:
        cmd = input("input cmd: ")
        cmds.append(cmd)
        if cmd == "exit":
            sys.exit()

    
# 受信したコマンドを実行する
def handle_cmd():
    global undo_cnt
    global cmds
    global recording
    global source
    if not cmds:
        return
    else:
        # print(cmds)
        cmd = cmds.pop()
        if cmd != "":
            source += f"\"{cmd}\",\n"
        cmd_args = cmd.split(" ")
        if cmd_args[0] == "move":
            if len(cmd_args) <= 9:
                print("[move] invalid args. usage: move [xmin xmax ymin ymax zmin zmax dx dy dz]")
                return
            func_args = [int(cmd_args_) for cmd_args_ in cmd_args[1:]]
            set(func_args[0], func_args[1], func_args[2], func_args[3], func_args[4], func_args[5], func_args[6], func_args[7], func_args[8])
            move()
        if cmd_args[0] == "set":
            if len(cmd_args) <= 9:
                print("[set] invalid args. usage: set [xmin xmax ymin ymax zmin zmax dx dy dz]")
                return
            func_args = [int(cmd_args_) for cmd_args_ in cmd_args[1:]]
            set(func_args[0], func_args[1], func_args[2], func_args[3], func_args[4], func_args[5], func_args[6], func_args[7], func_args[8])
        if cmd_args[0] == "exec":
            move()
        if cmd_args[0] == "reset":
            reset()
        if cmd_args[0] == "exit":
            global exited
            exited = True
            plotter.close()
            sys.exit()
        if cmd_args[0] == "undo":
            undo_cnt += 1
            undo()
        else:
            undo_cnt = 0
        if cmd_args[0] == "func":
            if len(cmd_args) >= 2:
                if cmd_args[1] in funcs.keys():
                    cmds = funcs[cmd_args[1]] + cmds
                    return
            print("[func] invalid args. usage: func [func_name]")   
        if cmd_args[0] == "recstart":
            if len(cmd_args) <= 1:
                print("[record] invalid args. usage: recstart [file_name]")
                return
            plotter.open_movie(f"../videos/{cmd_args[1].split(".")[0]}.mp4", framerate=int(1/dt))
            recording = True
        if cmd_args[0] == "recend":
            recording = False
        if cmd_args[0] == "clear":
            cmds = []
        if cmd_args[0] == "source":
            print(f"\n{source}")
        if cmd_args[0] == "delay":
            if len(cmd_args) <= 1:
                print("[delay] invalid args. usage: delay [time]")
                return
            delay(float(cmd_args[1]))
            


# statesの容量が無限に増え続けないようにする
def manage_states_num():
    global states
    global progress
    if len(states) <= MAX_STATES_NUM:
        return
    n = len(states) - MAX_STATES_NUM
    del states[:n-1]
    progress = np.max(progress - n + 1, 0)
    

# main
def main():
    global plotter
    global cmds
    init()
    # cmds.append("func 3dconveyor1")
    threading.Thread(target=receive_cmd, daemon=True).start()
    while True:
        handle_cmd()
        if not plotter._closed:
            plotter.update()
        manage_states_num()

    
if __name__=="__main__":
    main()