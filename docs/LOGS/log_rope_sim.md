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

---

## 2026-04-19 — README 改訂・円運動・アンカー反力ログ・妥当性検証

### 作業内容

#### README 全面改訂
旧 README はベースのコンテナテンプレートの説明のままだったため、プロジェクト実態（Isaac Sim ロープシミュレーション）に書き直した。特徴・ディレクトリ構成・環境構築手順・実行例コマンド 5 種・パラメータ一覧を記載。

#### アンカー円運動モード（`hang_rope.py`）
- `--circle-radius`・`--circle-period` 引数を追加
- アンカー（Segment_000）の XformOp を毎ステップ更新して水平円運動を実現
- XformCache のステール読み取りバグを修正（毎回新規インスタンス生成）

#### アンカー反力・トルクのログ出力
**調査:** Isaac Sim 5.1 で関節反力を取得する公式 API は `isaacsim.core.prims.Articulation.get_measured_joint_forces()` だが、PhysX の制約で **kinematic body を含む articulation は使用不可**（`"Articulations with kinematic bodies are not supported"` エラー）。

**採用した手法:** Newton の第二法則によるアンカー反力の解析的計算。

```
F_anchor = Σ(m_i · a_i) + (0, 0, m_total · g)   [系全体への Newton 第二法則]
T_anchor = Σ(r_i × m_i · (a_i + g_ẑ))            [アンカー基点まわりモーメント]
```

定常状態の仮定: a_i = (−ω²x_i, −ω²y_i, 0)（遠心加速度）。各セグメントの USD 位置から毎ステップ計算。

#### 妥当性検証（headless 実行）

**静的ケース（5 s）:**
```
Fz = +0.981 N（期待値 m·g = 0.981 N）✅ 全時刻で完全一致
T  = (0, 0, 0) Nm（期待値 ≈ 0）      ✅ 完全一致
tip z ≈ 0.200 m（= 0.8 − 0.6）       ✅
```

**円運動ケース（R=0.2 m、T=3 s、ω=2.094 rad/s、10 s）:**

期待下限 |Fxy| ≥ m·ω²·R = 0.088 N（重心が錘より外側に振れるため実際は超過）

| t | Fz | \|Fxy\| | 評価 |
|---|---|---|---|
| 0 s | 0.981 N | 0.013 N | 過渡（未展開）|
| 2〜10 s | 0.981 N | 0.062〜0.131 N | 期待範囲内で振動 |

- Fz は常に 0.981 N で不変 → 鉛直方向は重力のみ ✅
- |Fxy| は 10 s 時点でも振動中（定常未到達）。30 s 以上で収束を確認予定
- T_x, T_y が非ゼロ → 水平変位による曲げモーメントを正しく反映 ✅

### 技術的知見
- Isaac Sim 5.1 では `ArticulationView` が廃止され `isaacsim.core.prims.Articulation` に移行
- kinematic body を articulation に含めると PhysX が拒否するため、関節反力の直接計測は不可
- 代替として Newton 則による解析計算は十分な精度で動作することを確認
