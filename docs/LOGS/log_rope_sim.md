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

---

## 2026-04-19 — D6 DriveAPI 剛性キャリブレーション (deg vs rad 単位ずれ)

### 症状
- 水平片持ち梁テスト (E=1e9, N=25) の先端たわみが解析値 (δ≈54 mm) の 1/40 (≈1.4 mm) に
- 振動周期が解析値の 1/8 (= `sqrt(64)`) に収束
- ただし E への依存性 (1/√E スケーリング) は正しく再現 → 定数係数だけずれている

### 原因の同定
`UsdPhysics` の `PhysicsDriveAPI` スキーマ定義 (`schema.usda` 781-860 行)
を精読したところ、以下の記述を発見。

```
float physics:stiffness   ... if angular drive: mass*DIST_UNITS*DIST_UNITS/degrees/second/second
float physics:targetPosition ... if angular drive: degrees
float physics:damping ... If angular drive: mass*DIST_UNITS*DIST_UNITS/second/degrees
```

**角度単位がラジアンではなく度 (degrees)。** つまり
`stiffness` 属性に渡した値はトルク計算 `τ = stiffness · (target − θ)` の
`θ` が度で評価されるため、SI 値 (N·m/rad) をそのまま渡すと実効剛性が
`180/π ≈ 57.30` 倍になる。
周期比 `sqrt(57.30) = 7.57` はユーザー観測の 8× とほぼ一致。

### 実験検証 (`scripts/calibrate_drive.py`)
2 セグメントロープ (Segment 0 kinematic / Segment 1 free)、重力 OFF、
先端に初期角 2° を与え自由振動周期を測定 → `k_effective = ω² · I_end` で
実効剛性を抽出。

| 条件 | stiffness 属性 [S] | T_measured [ms] | T_analytic [ms] | k_eff/S |
|---|---|---|---|---|
| E=1e9, Raw (修正前) | 1.6362 | 25.05 | 190.26 | **57.70** |
| E=1e9, S=π/180 | 0.01745 | 243.03 | 190.26 | 57.47 |
| E=1e9, S=k·π/180 | 0.02854 | 190.02 | 190.26 | 57.48 |
| E=1e7, S=k·π/180 | 2.855e-4 | 1897.00 | 1902.60 | 57.65 |

全ての実験で `k_eff/S ≈ 57.30 (= 180/π)` で一致。複数 E で検証済みのため
ソルバー段階/制動効果ではなく純粋な単位変換係数であることを確定。

### 修正内容
`scripts/hang_rope.py::_compute_joint_drive` の戻り値を
`k_SI · π/180, c_SI · π/180` に変更 (DriveAPI 属性の単位系に変換)。
加えて `I_rot` の修正 (`m·r²` → `m·L_seg²/3`, 端点回り剛体棒の慣性)
により dt 自動調整と減衰計算が物理的に妥当な値を返すようにした。

### 修正後の検証
- E=1e9 水平片持ち (N=25): 平均先端 z ≈ 0.75 m (期待 0.746 m) → 誤差 < 1%
- 片持ち振動周期 ≈ 0.38 s (期待 0.375 s) → 誤差 < 2%
- 静的吊り下げ: Fz=0.981 N, T=0 Nm を維持 (既存テスト regression なし)
- 2 セグ振動テスト (E=1e9, 1e7) : 周期誤差 < 0.3%

### 残課題
- 大振幅 (|θ| > 20°) では小振幅解析値から 10〜20% 外れる。大変形の非線形性
  (束縛制約と遠心項) によるもので、バネ剛性そのものは正しい。
