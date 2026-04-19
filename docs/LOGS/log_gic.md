# Log: gic

## 2026-04-19 — GIC devcontainer セットアップ

### 目標
NeurIPS 2024 Oral の研究実装 [GIC (Gaussian-Informed Continuum)](https://github.com/Jukgei/gic) を、既存の Isaac Sim 5.1.0 devcontainer と同じ workspace で VS Code devcontainer として動かす環境を構築する。

### リポジトリ調査結果

GIC は多視点動画から変形物体の物性パラメータを推定し、物理ベースのビデオ合成を行うシステム。

| 技術 | 詳細 |
|------|------|
| 動的シーン表現 | 3D Gaussian Splatting |
| 物理シミュレーション | Material Point Method (MPM) via Taichi |
| 物性推定 | 微分可能シミュレーションで Young's modulus (E), Poisson's ratio (nu) を最適化 |
| 対応マテリアル | 弾性体 / 粘性流体 / 弾塑性 / 粒状体(砂) |

GIC の要求環境: Python 3.9 / PyTorch 2.4.0+cu121 / CUDA 12.1 / taichi 1.2.0。CUDA 拡張 3 本 (`diff-gaussian-rasterization`, `simple-knn`, `pytorch3d`) は nvcc でのソースビルドが必要。

### コンテナ実行可否の調査

現行の Isaac Sim コンテナ (Python 3.11 / torch 2.7+cu128 / nvcc なし) は GIC を動かせない。
- nvcc がないため CUDA 拡張をビルドできない
- taichi 1.2.0 は PyPI から除去済み（最新: 1.7.4）

ホスト環境: Ubuntu 24.04 / NVIDIA driver 575.57.08 (CUDA 12.9 対応) / RTX 3090 24GB。
`nvidia/cuda:12.1.0-devel-ubuntu22.04` ベースの専用コンテナであれば動作可能と判断。

### taichi バージョン対応

`environment.yml` が指定する `taichi==1.2.0` は PyPI から入手不可のため `1.7.4` を採用。
API 差分は 1 箇所: `ti.init(..., device_memory_fraction=0.5)` は 1.7.4 で `DeprecationWarning` だが動作する（`train_dynamic.py:342`）。

### 実装内容

VS Code のマルチ devcontainer 機構（`.devcontainer/` サブディレクトリ方式）を使い、`isaac-sim` と `gic` をピッカーで切り替え可能にした。

| 操作 | ファイル |
|------|---------|
| 移動+修正 | `.devcontainer/devcontainer.json` → `.devcontainer/isaac-sim/devcontainer.json` |
| 新規 | `.devcontainer/gic/devcontainer.json` |
| 新規 | `docker/Dockerfile.gic` |
| 新規 | `docker/requirements.gic.txt` |
| 新規 | `docker/entrypoint.gic.sh` |
| 編集 | `docker/docker-compose.yaml`（gic サービス追記、`profiles: ["gic"]`） |
| 編集 | `.dockerignore`（whitelist に新規 3 ファイル追加） |

**Dockerfile.gic のレイヤ順序:**
1. apt system packages (zsh, build-essential, cmake, ninja-build, ffmpeg, GL/X11 libs)
2. pip upgrade
3. PyTorch 2.4.0+cu121（CUDA 拡張のビルド前に必須）
4. CUDA build env (`CUDA_HOME`, `FORCE_CUDA=1`, `TORCH_CUDA_ARCH_LIST="8.6+PTX"`, `MAX_JOBS=8`)
5. pip deps from requirements.gic.txt（taichi 1.7.4 等）
6. torch-scatter（PyG wheel index で prebuilt wheel を使用）
7. git CUDA 拡張 3 本（個別レイヤ、pytorch3d は最後）
8. 非 root ユーザー作成

**`profiles: ["gic"]`** により `docker compose up -d` は Isaac Sim のみ起動する既存挙動を維持。VS Code devcontainer はサービス名指定でプロファイル制約を回避する。

### 既知の注意点

- 初回ビルド: **60〜90 分**、イメージ **~12〜15 GB**、docker 空き容量 **25 GB 以上**必要
- pytorch3d ビルドに `--no-build-isolation` 必須（setup.py が `import torch` するため）
- mmcv 2.1.0 ビルド失敗時は OpenMMLab 公式 wheel index にフォールバック
- GIC は config パスを repo root 相対で解決 → `cd /workspace/gic` が実行前提（`cdgic` エイリアス設定済み）
