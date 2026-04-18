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

### コンテナ UID 方針
方針 A 採用：runtime uid=1000 を維持し、Dockerfile で `/isaac-sim/kit/{cache,data,logs}` を
`mkdir -p` + `chown HOST_UID:HOST_GID` で事前作成する。
