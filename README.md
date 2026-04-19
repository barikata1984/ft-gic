# Rope Hanging Simulation

NVIDIA Isaac Sim 上で、重力下に吊り下がるロープの物理シミュレーションを行うプロジェクト。

剛体カプセルを球面ジョイント（SphericalJoint）で連結したロープモデルを USD（Universal Scene Description）で構築し、PhysX エンジンによる剛体シミュレーションを実行する。

## 特徴

- **ロープモデリング**: 剛体カプセルを球面ジョイントで連結した質量分散モデル
- **静的吊り下げ**: 固定アンカーからロープが重力下で垂れ下がる動態を計算
- **アンカー円運動**: アンカーポイントが水平面内を円運動するモードを搭載
- **GUI / ヘッドレス両対応**: ビジュアル確認用 GUI モードとバッチ処理用ヘッドレスモード

## ディレクトリ構成

```
.
├── .devcontainer/
│   └── devcontainer.json       # VS Code DevContainer 設定（Claude Code 等の拡張込み）
├── docker/
│   ├── Dockerfile              # Isaac Sim 5.1 NGC ベースイメージ
│   ├── docker-compose.yaml     # GPU・ボリューム・ipc: host
│   └── entrypoint.sh           # zsh 初期化 + gosu による非 root 切替
├── scripts/
│   ├── hang_rope.py            # シミュレーションメインスクリプト
│   ├── run_gui.sh              # GUI モード起動ラッパー
│   └── run_headless.sh         # ヘッドレスモード起動ラッパー
├── src/
│   └── rope_sim/
│       └── rope_builder.py     # RopeBuilder / RopeConfig 実装
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

コンテナ内で以下のコマンドを実行する。`run_gui.sh` / `run_headless.sh` はそれぞれ PYTHONPATH の設定と Isaac Sim の Python インタープリタ（`/isaac-sim/python.sh`）への委譲を行うラッパー。

### GUI モード（デフォルト設定）

```bash
scripts/run_gui.sh
```

### ヘッドレスモード（デフォルト設定・5秒間シミュレーション）

```bash
scripts/run_headless.sh
```

### ロープのパラメータを変更する

```bash
# 長さ 1.0m・直径 2cm・質量 0.3kg のロープ
scripts/run_gui.sh \
    --rope-length 1.0 \
    --rope-diameter 0.02 \
    --rope-mass 0.3
```

### セグメント数・スイング制限を調整する

```bash
# 50 セグメント・最大スイング角 45° に設定
scripts/run_headless.sh \
    --segments 50 \
    --swing-limit 45.0
```

### アンカーを円運動させる

```bash
# 半径 0.2m・周期 2.0s の円運動、シミュレーション時間 10 秒
scripts/run_headless.sh \
    --circle-radius 0.2 \
    --circle-period 2.0 \
    --duration 10.0
```

### アンカー高さと物理タイムステップを変更する

```bash
# アンカー高さ 1.2m・タイムステップ 1/120 s
scripts/run_gui.sh \
    --anchor-height 1.2 \
    --dt 0.00833
```

## パラメータ一覧

| パラメータ | デフォルト | 説明 |
|---|---|---|
| `--rope-length` | `0.6` m | ロープ全長 |
| `--rope-diameter` | `0.01` m | ロープ直径 |
| `--rope-mass` | `0.1` kg | ロープ総質量 |
| `--segments` | `25` | 剛体セグメント数 |
| `--swing-limit` | `60.0` deg | セグメント間の最大スイング角 |
| `--anchor-height` | `0.8` m | アンカー固定点の高さ |
| `--dt` | `1/60` s | 物理タイムステップ |
| `--duration` | `5.0` s | シミュレーション時間（ヘッドレスのみ） |
| `--circle-radius` | `0.0` m | アンカー円運動の半径（0 = 静止） |
| `--circle-period` | `3.0` s | アンカー円運動の周期 |
