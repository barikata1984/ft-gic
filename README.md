# Rope Hanging Simulation

NVIDIA Isaac Sim 上で、重力下に吊り下がるロープの物理シミュレーションを行うプロジェクト。

剛体カプセルを D6 ジョイント（角度ドライブ付き）で連結したロープモデルを USD で構築し、PhysX エンジンによる剛体シミュレーションを実行する。ヘッドレスオフスクリーンレンダリングによる MP4 動画出力にも対応。

## 特徴

- **ロープモデリング**: 剛体カプセルを D6 ジョイントで連結した質量分散モデル（Euler-Bernoulli 梁理論に基づく剛性計算）
- **充填率モデル**: `--fill-factor φ` により撚り・編組ロープの空隙を I_eff = I_solid × φ で表現（材料 E はナイロン本来値 1e9 Pa を維持）
- **静的吊り下げ**: 固定アンカーからロープが重力下で垂れ下がる動態を計算
- **アンカー円運動**: アンカーポイントが水平面内を円運動するモードを搭載
- **GUI / ヘッドレス両対応**: ビジュアル確認用 GUI モードとバッチ処理用ヘッドレスモード
- **オフスクリーン動画録画**: カメラセンサによるヘッドレス MP4 録画（`scripts/record_rope.py`）

## ディレクトリ構成

```
.
├── .devcontainer/
│   └── devcontainer.json       # VS Code DevContainer 設定
├── docker/
│   ├── Dockerfile              # Isaac Sim 5.1 NGC ベースイメージ
│   ├── docker-compose.yaml     # GPU・ボリューム・ipc: host
│   └── entrypoint.sh           # zsh 初期化 + gosu による非 root 切替
├── scripts/
│   ├── hang_rope.py            # シミュレーションメインスクリプト（GUI / ヘッドレス）
│   ├── record_rope.py          # オフスクリーン MP4 録画スクリプト
│   ├── run_gui.sh              # GUI モード起動ラッパー
│   ├── run_headless.sh         # ヘッドレスモード起動ラッパー
│   └── run_record.sh           # 動画録画起動ラッパー
├── src/
│   └── rope_sim/
│       └── rope_builder.py     # RopeBuilder / RopeConfig 実装
├── debug/                      # 録画出力先（.gitignore 対象）
└── pyproject.toml
```

## 環境構築

### 前提条件

- Docker + NVIDIA Container Toolkit
- VS Code + Dev Containers 拡張（推奨）

### 起動方法

**VS Code (DevContainer)**:

コマンドパレット → `Dev Containers: Reopen in Container`

**CLI**:

```bash
cd docker
docker compose build
docker compose up -d
docker compose exec dev zsh
```

## 実行例

コンテナ内で以下のコマンドを実行する。各シェルスクリプトは PYTHONPATH の設定と Isaac Sim の Python インタープリタ（`/isaac-sim/python.sh`）への委譲を行うラッパー。

### GUI モード（デフォルト設定）

```bash
scripts/run_gui.sh
```

### ヘッドレスモード（デフォルト設定・5秒間シミュレーション）

```bash
scripts/run_headless.sh
```

### アンカーを円運動させる（GUI）

```bash
# 半径 0.1m・周期 3.0s の円運動
scripts/run_gui.sh \
    --circle-radius 0.1 \
    --circle-period 3.0
```

### アンカーを円運動させる（ヘッドレス・10秒間）

```bash
scripts/run_headless.sh \
    --circle-radius 0.1 \
    --circle-period 3.0 \
    --duration 10.0
```

### オフスクリーン動画録画（debug/ に MP4 出力）

```bash
# デフォルト設定（静止アンカー、10秒、30fps）
scripts/run_record.sh --duration 10

# 円運動ありで録画
scripts/run_record.sh \
    --circle-radius 0.1 \
    --circle-period 5.0 \
    --duration 15
```

出力先: `debug/<timestamp>_rope[_circle_r<R>].mp4`

### ロープのパラメータを変更する

```bash
# 長さ 1.0m・直径 2cm・質量 0.3kg のロープ
scripts/run_gui.sh \
    --rope-length 1.0 \
    --rope-diameter 0.02 \
    --rope-mass 0.3
```

### 充填率を変更する（柔らかさの調整）

```bash
# φ=0.01（柔らかいロープ、等価実効 E ≈ 1e7 Pa）
scripts/run_record.sh \
    --fill-factor 0.01 \
    --circle-radius 0.1 \
    --circle-period 5.0 \
    --duration 15
```

## パラメータ一覧

### ロープ物性

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `--rope-length` | `0.6` m | ロープ全長 |
| `--rope-diameter` | `0.01` m | ロープ直径 |
| `--rope-mass` | `0.1` kg | ロープ総質量 |
| `--youngs-modulus` | `1e9` Pa | ナイロン繊維のヤング率（材料値、変更不要） |
| `--fill-factor` | `0.3` | 断面充填率 φ（0〜1）。I_eff = I_solid × φ。撚りロープ: 0.01〜0.5 |
| `--damping-ratio` | `0.3` | ジョイント減衰比 ζ（0=無減衰, 1=臨界減衰） |

### シミュレーション設定

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `--segments` | `25` | 剛体セグメント数 |
| `--swing-limit` | `60.0` deg | セグメント間の最大スイング角 |
| `--anchor-height` | `0.8` m | アンカー固定点の高さ |
| `--dt` | `1/60` s | 物理タイムステップ（omega_n に応じて自動縮小） |
| `--duration` | `5.0` s | シミュレーション時間（ヘッドレス・録画のみ） |

### アンカー円運動

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `--circle-radius` | `0.0` m | アンカー円運動の半径（0 = 静止） |
| `--circle-period` | `3.0` s | アンカー円運動の周期 |

### 録画設定（`record_rope.py` のみ）

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `--fps` | `30` | 動画フレームレート |
| `--width` | `1280` px | 動画横解像度 |
| `--height` | `720` px | 動画縦解像度 |
| `--output` | 自動生成 | 出力 MP4 パス（省略時: `debug/<timestamp>_rope*.mp4`） |

## 剛性モデルについて

ジョイント曲げ剛性は Euler-Bernoulli 梁理論から計算する：

```
k_bend = E · I_eff / L_seg
I_eff  = (π · r⁴ / 4) · φ
```

- **E**: ナイロン繊維の弾性率（1e9 Pa）— 材料固有値、変更しない
- **φ**: 充填率（`--fill-factor`）— ロープの撚り・編組による空隙を表現
- **I_eff**: 実効断面二次モーメント — φ=1 が中実棒、φ<1 がロープ

φ の目安:

| φ | 挙動 | 等価実効 E |
|---|---|---|
| 1.0 | ナイロン中実棒 | 1e9 Pa |
| 0.3 | 撚りロープ（標準） | 3e8 Pa |
| 0.01 | 柔らかいロープ | 1e7 Pa |
