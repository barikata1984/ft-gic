# PLAN

## ロープシミュレーション設計方針

### 物理手法
剛体カプセルチェーン + SphericalJoint を採用。

- D6 ジョイントは rotX/rotY 同時制限が PhysX 5 の "double pyramid mode" 非対応でエラー
- SphericalJoint（`CreateConeAngle0/1LimitAttr`）で揺れ角を制限、ねじり自由
- FEM デフォーマブルボディは細長いロープに不適（体積的変形）

### ディレクトリ構成
Python Packaging User Guide 推奨の src レイアウト。

```
src/rope_sim/        # ライブラリ（他コードから import 可能）
scripts/             # CLI エントリポイント・シェルスクリプト
```

実行は `/isaac-sim/python.sh` + `PYTHONPATH=src` でパッケージ解決。`pip install -e .` は不要。

### headed / headless 切り替え
`SimulationApp({"headless": args.headless})` で統一。`--headless` フラグで切り替え。

### ログ出力
`print()` は Isaac Sim の stdout に埋もれるため `carb.log_warn("[rope] ...")` を使用。
`2>&1 | grep "\[rope\]"` でフィルタリング可能。

---

## GIC devcontainer 設計方針

### コンテナ分離戦略
Isaac Sim (Python 3.11 / torch 2.7+cu128) と GIC (torch 2.4+cu121 / taichi / CUDA 拡張) は依存が衝突するため、**専用コンテナを分離**する。

- ベースイメージ: `nvidia/cuda:12.1.0-devel-ubuntu22.04`（nvcc 12.1 同梱）
- `docker compose` の `profiles: ["gic"]` で Isaac Sim 既定起動に影響を与えない
- VS Code マルチ devcontainer: `.devcontainer/isaac-sim/` と `.devcontainer/gic/` のサブディレクトリ方式

### pip インストール順序
torch を先にインストールしないと CUDA 拡張の `setup.py` が失敗するため、Dockerfile のレイヤ順序は固定:
1. PyTorch 2.4.0+cu121
2. 通常 pip deps（taichi 等）
3. torch-scatter（PyG wheel index）
4. git CUDA 拡張 3 本（個別レイヤ、pytorch3d は最後）

### taichi バージョン
`environment.yml` 指定の 1.2.0 は PyPI から除去済み → **1.7.4** を採用。`device_memory_fraction` は deprecated だが動作する（修正不要）。

### CUDA arch
RTX 3090 = compute 8.6 → `TORCH_CUDA_ARCH_LIST="8.6+PTX"`。GPU 変更時は Stage 7 の 3 レイヤを再ビルド。

### コンテナ UID 方針
方針 A 採用：runtime uid=1000 を維持し、Dockerfile で `/isaac-sim/kit/{cache,data,logs}` を
`mkdir -p` + `chown HOST_UID:HOST_GID` で事前作成する。
