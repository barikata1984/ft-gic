# Log: rope_sim

## 2026-04-18 — 剛体チェーンによるロープ吊り下げシミュレーション 初期実装

### 目標
Isaac Sim 5.1 上でロープ（全長 60cm、直径 1cm、質量 100g）を空中に垂らすシミュレーションを実装。headed / headless 両対応、CLI でパラメータを設定可能にする。

### 手法調査結果
- **採用:** 剛体カプセルチェーン + SphericalJoint
- **不採用:** D6 ジョイント（PhysX 5 で rotX/rotY 同時制限が "double pyramid mode" エラー）
- **不採用:** FEM デフォーマブルボディ（体積的変形で細いロープに不向き）

### 実装
```
src/rope_sim/__init__.py
src/rope_sim/rope_builder.py   # RopeConfig dataclass + RopeBuilder クラス
scripts/hang_rope.py           # CLI エントリポイント（argparse + SimulationApp）
scripts/run_gui.sh             # headed 起動
scripts/run_headless.sh        # headless 起動
pyproject.toml
```

### 動作確認結果
**headless:**
```
t= 0.00s  tip=(+0.0000, +0.0000, +0.1977) m
t= 1.00s  tip=(+0.0000, +0.0000, +0.1995) m
...（5秒間安定）
```
アンカー高さ 0.8m − 全長 0.6m = **0.2m**（理論値）と一致。

**GUI（headed）:** 起動・表示を確認。ユーザーがウィンドウを閉じて正常終了。

### 発見した問題
- `/isaac-sim/kit/cache/` 等が uid=1234（isaac-sim）所有で uid=1000 からは書き込み不可
- DerivedDataCache（UJITSO）が機能せずアセット処理に支障
- Dockerfile に3ディレクトリの `mkdir + chown` を追加済み。コンテナリビルドで解消予定
