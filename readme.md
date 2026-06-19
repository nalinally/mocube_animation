# これは何

研究用のアニメーション描画プログラムです

# 環境構築

`setup.sh`は実行すると勝手にvenvが入りますので、嫌な人は別の方法での環境構築を試みてください
```
$ git clone https://github.com/nalinally/mocube_animation.git
$ cd mocube_animation
$ source setup.sh
```

# 実行方法

```
cd modube_animation
source activate_venv.sh  # setup.sh実行した人のみ
cd scripts
python3 main.py  # source launch.shでも可
```

うまく実行できるとこんな感じの画面になります
![alt text](figures/image.png)

プログラムは対話的に動かしていきます。実行しただけではただの8x8x8のキューブが表示されるだけです。最初の状態では、6<=x<=14, 6<=y<=14, 6<=z<=14の領域がキューブで満たされています。以下が関数です。`[]`は引数であることを表しますが、実際に実行するときには不要です。

- `move [xmin xmax ymin ymax zmin zmax dx dy dz]`
    - 指定した直方体領域を指定した分だけ動かせます。x軸->y軸->z軸の順で動かしていきます。

- `set [xmin xmax ymin ymax zmin zmax dx dy dz]`
    - 動きを予約します。`exec`を実行すると、`set`されたすべての動きが同時に行われます。引数の意味はmoveと同じです

- `exec`
    - `set`された動きを実行します

- `reset`
    - 最初の状態に戻します

- `clear`
    - 実行中の動きをすべてキャンセルします

- `func [func_name]`
    - あらかじめ登録された一連の動きを実行します。動きは`scripts/func.py`に登録できます。

- `exit`
    - 終了します。

- `undo`
    - ひとつ前の状態に戻します

- `recstart`, `recend`
    - `recstart`で録画開始、`recend`で録画終了です。画面録画ではなく、録画中に表示された各フレームをある時間ずつ表示する動画を生成します。動画は`videos/`の中に生成されます。

- `delay [duration]`
    - 待ち時間を生成します。録画中に有用です。

# 実行例

例えばこのような動画を作ることができます。

