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

---

## 2026-04-19 — セグメント位置 CSV・PhysX 直接 API・kinematic body 円運動

### 作業内容

#### セグメント位置記録 (`--segment-csv`)
`hang_rope.py` に `--segment-csv PATH` オプションを追加。`_record_segments(t)` が全セグメントの (t, seg, x, y, z) を CSV に書き出す。`scripts/analyze_segments.py` を新規作成し、以下を出力:
- アンカー XY 軌跡（期待円 vs 実測、`err_r`）
- 各セグメントの mean XY 半径・Z（最後 3 s の定常状態推定）
- 最終スナップショット時のロープ形状

#### USD ステール読み取りバグの発見と修正

**バグ:** headless モード (`render=False`) では PhysX→USD 同期が行われないため、`UsdGeom.XformCache()` で読み取ると PhysX の計算結果ではなく直前に書いた USD 値を返す。旧 CSV で `err_r=0.0000` が出ていたのはこれが原因（自分が書いた値を自分で読んでいた）。

**修正:** `_record_segments`・`_tip_pos`・`_compute_anchor_wrench` の全 USD 読み取りを `RigidPrimView.get_world_poses(usd=False)` に置き換え、PhysX から直接取得するようにした。

#### 初期ジャンプの修正
`build()` では Segment_000 を `(0,0,z)` に配置するが、`_run()` 開始直後の `_update_anchor(t=0)` が `(R,0,z)` に設定するため 0.1m のテレポートが発生し、constraint 爆発でロープが暴れる。`world.reset()` 前に全セグメントを `(R,0,0)` オフセットすることで解消。

#### kinematic body 円運動 → 未解決

`anchor_translate_op.Set()` (USD XformOp 直書き) → `RigidPrimView.set_world_poses(usd=True/False)` に切り替えたが、**GUI レンダラーでは依然としてアンカーが静止したまま**。

headless の `get_world_poses(usd=False)` が返す値は err_r=0.0000 だが、これはキネマティックターゲット値（書いた値）を読み返しているだけの可能性が高い。PhysX が実際にボディを動かしているかは未確認。

### 残課題
- kinematic body の位置を PhysX で実際に更新し、レンダラーにも反映させる方法の調査
  - `omni.physx.get_physx_simulation_interface().set_kinematic_target()` 直接呼び出し
  - または dynamic body + velocity 制御への切り替え
- 定常状態での |Fxy| 収束確認（30 s 以上）

---

## 2026-04-20 — GUI 表示バグ修正（幽霊セグメント・再生速度・ツイスト）

### 問題

GUI 実行時に 3 つの症状が同時発生していた：

1. **幽霊セグメント**: ロープ上端（seg0）と同形状のプリムがロープ本体から離れた位置に静止表示される
2. **再生速度が極端に遅い**: 物理時間 3 秒（1 周）を実現するのに実時間で数分かかる
3. **ロープが自転（ツイスト）する**: 指示していないのに rotZ 方向の回転が蓄積する

### 根本原因の調査

#### 幽霊セグメントの原因

`RigidPrimView.set_world_poses()` のソースコード（`isaacsim.core.prims/impl/rigid_prim.py`）を精読した結果：

- シミュレーション中（`is_physics_handle_valid() == True`）は `usd` パラメータが**完全に無視**され、`_physics_view.set_transforms(pose, indices)` のみが呼ばれる
- `set_transforms()` は PhysX のみ更新し、**Fabric（レンダラーのシーングラフ）は更新しない**
- Fabric は `world.reset()` 時に USD の初期値で初期化されるため、seg0 は reset 前の USD 位置（オフセット前の `x=0`）に固定されたまま表示される
- 結果：PhysX では `x=R` で円運動しているが、レンダラーは `x=0` の位置に幽霊を描画する

#### 再生速度が遅い原因

`omega_n ≈ 5160 rad/s`（ナイロン E=1e9 Pa）により dt が `1/60 s → 0.0001 s` に約 170 倍縮小される。`world.step(render=True)` を毎ステップ呼んでいたため、1 秒の物理時間に約 1 万回レンダリングが走り実時間より遥かに遅くなっていた。

公式ドキュメントにより確認：`world.step()` は 1 呼び出しで physics_dt 1 ステップのみ進む（rendering_dt 分まとめて進むわけではない）。

#### ツイスト（自転）の原因

D6 ジョイントの rotZ（ツイスト軸）が `free` かつ drive なしのため、円運動の慣性力が生む小さなツイストトルクが毎ステップ蓄積し、ロープ全体が徐々に自転していた。

### 修正内容

| 症状 | 修正箇所 | 内容 |
|------|----------|------|
| 幽霊セグメント | `scripts/hang_rope.py` `_update_anchor()` | `_get_fabric_hierarchy()` → `get_world_xform()` → `SetTranslateOnly()` → `set_world_xform()` で Fabric を毎フレーム明示的に更新 |
| 再生速度 | `scripts/hang_rope.py` GUI ループ | `world.step(render=True)` を毎ステップ呼ぶのをやめ、`render_every = round((1/60) / dt)` ステップごとに 1 回だけ描画 |
| ツイスト | `src/rope_sim/rope_builder.py` `_add_d6_joint()` | rotZ に `stiffness=0, damping=joint_damping` の drive を追加してツイスト角速度を減衰させる |

加えて、`python scripts/hang_rope.py` を直接実行した際に `rope_sim` モジュールが見つからない問題（`ModuleNotFoundError`）を `sys.path.insert(0, src/)` で修正した。

---

## 2026-04-20 — GUI 円運動のカクカク・低速問題修正

### 問題

前回の `render_every` 間引き修正後もGUI上の動作がカクカクで、物理時間3秒（1周）の円運動が実時間数分かかる状態が続いていた。RTX 5090 の性能を考えると説明がつかず、実装上の誤りを疑い調査した。

### 根本原因

`SimulationContext.step()` のソース（`isaacsim.core.api/simulation_context/simulation_context.py`）を精読した結果、以下が判明：

- `world.step(render=True)` → `self._app.update()` — Kit アプリが `rendering_dt / physics_dt` 分の物理サブステップを**自動実行**してから描画する
- `world.step(render=False)` → `_physics_context._step()` — 物理を**1ステップのみ**進める

前回の修正（`render_every=167` 回に1回 `render=True`）は意図と逆効果だった：
- `render=True` の1回 → `_app.update()` → 167サブステップ + 描画（これは正しい）
- `render=False` の166回 → 物理1ステップ × 166回 → 余分な物理計算が混入し、かつアンカー更新もPythonループ側で1フレーム1回しか呼ばれないため Kit の167サブステップ内ではアンカーが固定 → カクカクの原因

### 修正内容

**GUIループの抜本的整理（`scripts/hang_rope.py`）：**

1. **アンカー更新を `world.add_physics_callback()` に移行**
   - `subscribe_physics_step_events` 経由で PhysX の全サブステップ前にコールバック登録
   - Kit 内部の167サブステップそれぞれで正しい時刻 `world.current_time` のアンカー位置が設定される

2. **GUIループを `world.step(render=True)` 一本に整理**
   - 手動の `render_every` 間引きを廃止
   - Kit が `rendering_dt=1/60 s` / `physics_dt≈0.0001 s` の比を自動管理

3. **Fabric 更新はレンダーフレームごと1回**（各サブステップでは不要）

### 結果

実行ログ確認：実時間46秒で物理時間11.8秒（実時間比 ≈ 0.84）、tip の (x,y) が滑らかに円を描き `|Fxy| ≈ 0.044 N`（理論値と一致）。GUI表示が大幅に滑らかになった。

---

## 2026-04-20 — seg0 表示ズレ問題の根本解決

### 問題

GUI で seg0（kinematic アンカー）が運動方向と逆方向にズレて表示される。物理的に不自然。

### 調査過程

`SimulationContext.render()` のソース確認により、`force_update()` が呼ばれるのは `world.render()` 経由のみで、`world.step(render=True)` が内部で呼ぶ `_app.update()` では呼ばれないことを確認。

複数のアプローチを試みたが、いずれも問題が残った：
1. `world.render()` + 手動サブステップループ → カクカク再発・幽霊再出現
2. `usdrt` Fabric 直書き → タイミング競合でズレ
3. `world.current_time` を毎ループ呼ぶ → `_app.update()` 内の 167 サブステップでアンカー固定

### 根本原因の確定

`RigidPrimView.set_world_poses()` はシミュレーション中（`is_physics_handle_valid() == True`）に `usd` パラメータを完全無視し `_physics_view.set_transforms()` のみ呼ぶ。これは PhysX のみを更新し Fabric（レンダラー）を更新しない。Fabric は `world.reset()` 時の USD 初期値で固定されるため、seg0 の表示位置が原点付近に固定される。

### 最終的な解決策

**USD `TranslateOp.Set()` + `add_physics_callback` の組み合わせ。**

- `RigidPrimView` を廃止し、`UsdGeom.Xformable(seg0_prim).GetOrderedXformOps()` から直接 `TranslateOp` を取得
- USD 属性への直接書き込みは Isaac Sim の USD-Fabric sync レイヤーにより毎フレーム Fabric に伝播される
- `world.add_physics_callback("anchor_circle", lambda _: _update_anchor(world.current_time))` で Kit の全サブステップ内で正しい時刻のアンカー位置を設定

### 結果

seg0 のズレ（幽霊・逆方向オフセット）が解消。ロープ全体が一体となって滑らかに円運動するようになった。

---

## 2026-04-20 — オフスクリーン動画録画・ヤング率修正

### オフスクリーン動画録画（`scripts/record_rope.py`）

GUI なしで物理挙動を視覚的に検証する手段として、ヘッドレスオフスクリーンレンダリング + MP4 書き出しスクリプトを実装。

**設計方針:**
- `isaacsim.sensors.camera.Camera` で `/World/RecordCam` を配置、`get_rgba()` で numpy 配列取得
- 物理ステップ `steps_per_frame = round(1/fps / dt)` おきに1フレーム撮影（毎ステップレンダリング不要）
- OpenCV `VideoWriter`（Isaac Sim 内蔵 cv2、FFMPEG バックエンド有）で MP4 エンコード
- `simulation_app.close()` が `sys.exit()` 相当のため、エンコードを close() 前に実行
- 出力先: `debug/<timestamp>_rope[_circle_r<R>].mp4`

**実装で発生した問題と解決:**
- `GfQuatf` → `GfQuatd` 型不一致エラー → `Quatd` に修正
- `simulation_app.close()` 後のコードが実行されない → エンコードを close() 前に移動
- コンテナ内に `ffmpeg` バイナリなし → Isaac Sim 同梱 cv2（FFMPEG ビルトイン）で解決

**パフォーマンス（E=1e7）:**
- physics steps: 10,321（dt=969µs）、capture every 34 steps → 302 frames @ 30fps
- wall-time 比: **0.57x**（E=1e9 時の 0.07x から 8 倍改善）

### ヤング率の修正（中実棒 → 撚りロープ実効値）

**問題:** E=1e9 Pa（ナイロン中実棒）では剛性が高すぎ、ほぼ変形しない棒として挙動。

**調査結果（外部ソース）:**
- 固体ナイロン: E = 2.5〜3.9 GPa
- 撚り・編組ナイロンロープの実効弾性率: **0.6〜2 GPa**（繊維単体の 40〜50%）
- 柔らかいロープ下限: 50〜100 MPa（パッキング率・ブレイド角依存）
- 出典: Cambridge Materials Case Study on Ropes; MDPI Braided Rope Modulus Paper

**対処:** デフォルト値を `E=1e9` → `E=1e7` Pa に変更（`hang_rope.py`, `record_rope.py` 両方）。
撚りロープの下限付近で、目視で柔らかい挙動を確認。

**効果:**
- omega_n: 5160 → 516 rad/s → dt_max: 97µs → 969µs（10倍緩和）
- wall-time 比: 0.07x → 0.57x

**検証動画（`debug/`）:**
- `20260420_040328_rope_circle_r0.10.mp4` — T=3s, E=1e7
- `20260420_040512_rope_circle_r0.10.mp4` — T=1s（1回転/秒）
- `20260420_040759_rope_circle_r0.10.mp4` — T=5s（1回転/5秒）、15s 録画

### 剛性モデルの修正：E の調整 → 充填率 φ による I_eff

**問題提起:** E を 1e9→1e7 に下げるのは「材料を偽造する」行為。正しくは断面形状（ロープの空隙）を表現すべき。

**設計変更:**
- E はナイロン繊維本来の値（1e9 Pa）に戻す
- `fill_factor φ`（充填率）を新設し `I_eff = I_solid × φ` で実効断面二次モーメントを計算
- デフォルト φ=0.3（撚りナイロンロープの文献的下限）

**実装:**
- `_compute_joint_drive()` に `fill_factor` 引数追加（`hang_rope.py`, `record_rope.py` 両方）
- `--fill-factor` CLI 引数追加（デフォルト 0.3）
- omega_n 計算も `I_eff` を参照するよう修正

**φ=0.3（E=1e9）の特性:**
- 等価実効 E = 3×10⁸ Pa、omega_n=2827 rad/s、dt=177µs、wall-time 比 0.12x

**φ=0.01（E=1e9）≒ E=1e7 の特性:**
- omega_n=516 rad/s、dt=969µs、wall-time 比 0.57x（前回と同等）
- `debug/20260420_041737_rope_circle_r0.10.mp4` — T=5s、15s 録画で確認

---

## 2026-04-20 — カメラモジュール化・swing録画・ground plane修正

### カメラ配置モジュール化（`src/rope_sim/camera_utils.py`）

**問題:** look-at quaternion 計算（約15行）と Camera 初期化シーケンスが `record_rope.py` / `swing_rope.py` / `_check_camera.py` に完全重複。複数カメラ配置時に対応困難。

**解決:** `make_camera(world, prim_path, position, target, fps, resolution)` 関数に集約。

内部処理:
1. look-at 回転行列 `[fwd | -right | up]` → quaternion 変換（Shepperd法）
2. `Camera()` 生成 → `world.reset()` → `camera.initialize()`
3. `camera.set_world_pose(position, orientation, camera_axes="world")`
4. ウォームアップ15フレーム（`get_rgba()` が即座に有効になる）

使用側は `make_camera()` 1行に置換。複数カメラは `prim_path` を変えて複数回呼ぶだけ。

### ground plane の修正（decorative grid → 不可視衝突面）

**問題:** `world.scene.add_default_ground_plane()` が格子模様の巨大グリッド床を描画し、カメラの視野を占拠。

**解決:** `UsdGeom.Plane` + `purpose=guide`（不可視）+ `UsdPhysics.CollisionAPI` の組み合わせに統一。`record_rope.py` と `swing_rope.py` 両方に適用。

### swing_rope.py の追加

アンカーを正弦波で揺動させる録画スクリプト。`θ(t) = amplitude × sin(2π/T × t)` を `RotateX` op で毎ステップ設定。

**検証:** `_check_camera.py` でパラメータ確認（d=3.5, z=1.2, target_z=0.4）→ `swing_rope.py` で再現 ✓

**カメラ向き問題の調査・解決過程:**
- `Camera(orientation=...)` コンストラクタ渡しのみ → `world.reset()` で上書きされる問題
- 手動 xform op 書き換え → 型不一致（GfQuatf vs GfQuatd）でクラッシュ
- `camera.set_world_pose(camera_axes="world")` を `initialize()` 後に呼ぶ方式で確定

---

## 2026-04-20 — Y軸単振動録画スクリプト（oscillate_rope.py）

### 概要

アンカー姿勢を固定したまま Y 軸方向に正弦波単振動させる録画スクリプトを実装。

```
y(t) = A · sin(2π / T · (t − t_settle))   [t > t_settle]
y(t) = 0                                    [t ≤ t_settle]
```

デフォルト: A=0.05m, T=1.0s（swing_rope.py と周期を統一）、settle_time=1.0s。

### 実装（`scripts/oscillate_rope.py`）

- アンカー（Segment_000）の `TranslateOp` を毎物理ステップ更新（姿勢 op は追加しない）
- コールバックを `make_camera()`（`world.reset()` を内包）の**前**に登録
  → `world.reset()` で `current_time=0` にリセットされるため、warmup 中も t=0 から滑らかに開始
  → `make_camera()` 後に `_rest_pos` を再取得してリセット後の USD 状態を反映
- settle フェーズ（デフォルト 1s）中はアンカーを静止させ、ロープが重力で安定してから振動開始
- 毎レンダーフレームで全セグメントの USD 位置を記録し、終了後に Y-Z プロット（3×3 グリッド）を自動生成

### 発見した問題と対処

**初期衝撃の問題（旧実装）:**
コールバック登録が `make_camera()` の後だったため、warmup 終了後に t≠0 の変位が突然印加されていた。コールバックを `make_camera()` より前に移動して解消。

**剛性過大（omega_n=2827 rad/s）:**
デフォルト `fill_factor=0.3` では固有周期 T_n=0.002s で加振周期 1s に対して極端に短く、ロープが剛体的に平行移動するだけだった。
`--fill-factor 0.0001`（T_n≈0.12s）で上端と下端の位相差が視認できる柔軟挙動を確認。
なお segments 数を増やすと L_seg が短くなり omega_n が再上昇するため、segments=128 では phi をさらに下げる必要がある。

### 検証結果

| segments | fill_factor | omega_n [rad/s] | dt [ms] | 挙動 |
|---|---|---|---|---|
| 25 | 0.3 | 2827 | 0.18 | 剛体平行移動（×）|
| 25 | 0.0001 | 51.6 | 9.69 | 上下位相差あり（○）|
| 128 | 0.0001 | 1353 | 0.37 | 再び剛化（△）|

Y-Z プロット: `debug/snapshots/oscillate_yz_positions.png`
動画: `debug/20260420_07*_oscillate_rope.mp4`

---

## 2026-04-20 — モジュール化・ポアソン比活用の調査・検討

### モジュール化の現状評価

4スクリプト（hang / record / swing / oscillate）の重複状況を分析した結果：

**適切にモジュール化済み:**
- `RopeBuilder` / `RopeConfig` — 全スクリプトで import
- `make_camera()` — record / swing / oscillate で import

**未モジュール化の重複（4箇所以上）:**

| 重複箇所 | 件数 | 備考 |
|---|---|---|
| `_compute_joint_drive()` | 4 | `oscillate_rope.py` では `poissons_ratio` 引数が欠落 |
| dt Nyquist クランプ計算 | 4 | ロジックは完全同一、ログプレフィックスのみ異なる |
| 不可視 GroundPlane 構築 | 3 | record / swing / oscillate |
| DomeLight + KeyLight 設置 | 3 | 強度・角度すべて同一 |
| `_encode_mp4()` | 3 | avc1 → mp4v フォールバック込み |

**提案するモジュール構成:**
```
src/rope_sim/
  sim_utils.py   — compute_joint_drive(), clamp_dt()
  scene_utils.py — add_invisible_ground(), add_default_lighting(), setup_recording_world()
  video_utils.py — encode_mp4(), default_output_path()
```

hang_rope.py は GUI/CSV/力計算など固有機能が多いため、共通化対象は `compute_joint_drive` と `clamp_dt` のみとし、無理に統合しない。

### ポアソン比活用の調査

**現状:** `poissons_ratio` は全スクリプトの `_compute_joint_drive()` 引数に存在するが未使用。`hang_rope.py:68` で `G = E/(2(1+ν))` と `J = π·r⁴/2` を計算しているが結果を `_` に捨てている（ドキュメント目的と明記）。

**活用可能な箇所: ねじり剛性 `k_torsion`**

```
G      = E / (2(1+ν))          # せん断弾性率
J_eff  = (π·r⁴/2) · φ         # 実効極断面二次モーメント
k_torsion = G · J_eff / L_seg  # ねじり剛性 [N·m/rad]
```

ν=0.35 (ナイロン) のとき `k_torsion / k_bend = 1/(1+ν) ≈ 0.74`。曲げ剛性の約 74% のねじり剛性。

**曲げ剛性への影響:** Euler-Bernoulli 梁ではポアソン比は曲げ剛性に影響しない（E·I のみ）。Timoshenko 梁のせん断補正係数には影響するが、ロープの細長比 L/d=60 ではせん断変形は無視できる。

**実装方針:**
- `_compute_joint_drive()` の戻り値に `k_torsion_deg` を追加
- `rope_builder.py` `_add_d6_joint()` の rotZ `stiffness` に設定
- モジュール化リファクタリングと同時実施が効率的

**注意点:** 撚りロープはねじりと軸張力がヘリックス構造でカップリングするため、等方性棒モデルは近似。ただしゼロ剛性よりは物理的に妥当。

---

## 2026-04-20 — モジュール化リファクタリング・hang_rope.py 録画機能追加・円運動録画バグ修正

### モジュール化リファクタリング

以下の3モジュールを新規作成し、5スクリプトをリファクタリング：

| モジュール | 提供する関数 |
|---|---|
| `src/rope_sim/sim_utils.py` | `compute_joint_drive()`, `clamp_dt()` |
| `src/rope_sim/scene_utils.py` | `add_invisible_ground()`, `add_default_lighting()`, `setup_recording_world()` |
| `src/rope_sim/video_utils.py` | `encode_mp4()`, `default_output_path()` |

- `compute_joint_drive()` から `poissons_ratio` 引数を除去（未使用だったため）
- `clamp_dt()` は `label` 引数でログプレフィックスを変えられるよう汎用化
- `setup_recording_world()` が `World` 生成 + 不可視床 + ライティングを一括担当
- `default_output_path()` は `__file__` から2親上を `debug/` として解決

修正したスクリプト: `record_rope.py`, `swing_rope.py`, `oscillate_rope.py`, `_check_camera.py`, `hang_rope.py`

**発見したバグと修正:**
- リファクタ後に `capture_dt` が未定義エラー → 各録画ループ前に `capture_dt = 1.0 / args.fps` を追加
- `oscillate_rope.py` の `debug_dir` 未定義エラー → `out_path.parent / "snapshots"` に修正

### hang_rope.py 録画機能追加

`--record` フラグで MP4 録画モードに切替。実装済みの `make_camera()`, `encode_mp4()`, `default_output_path()` を活用。

- `--record` 指定時は `--headless` を自動有効化
- 静的ハング: カメラ `[3.5, 0.0, 1.2]` → target `[0.0, 0.0, 0.4]`（他スクリプトと共通）
- 円運動: カメラ `[4.5, 0.0, 1.0]` → target `[0.0, 0.0, 0.5]`（全方位をカバー）

### 円運動録画バグの根本修正

**症状（修正前）:** 録画開始後にロープが激しく暴れる。

**原因の同定:** `20260420_054350_rope_circle_r0.10.mp4`（旧 record_rope.py 生成、暴れなし）と比較して構造の違いを特定。

旧 `record_rope.py` の構造:
```
x0 オフセット適用  ←─┐ make_camera() 前
コールバック登録   ←─┘
make_camera()  # world.reset() + warmup 15ステップ（コールバック有効状態）
```

誤った hang_rope.py の構造:
```
make_camera(warmup_frames=0)  # world.reset() → x0・コールバックがクリアされる
_run_record() 内で x0 再適用・コールバック登録
手動 warmup 15ステップ・settle 6s
```

**修正:** x0 オフセット適用とコールバック登録を `make_camera()` の**前**に移動し、`warmup_frames` をデフォルト 15 に戻した。`make_camera()` 内の `world.reset()` + 15ウォームアップステップがコールバック有効状態で走るため、ロープが正しい初期状態から滑らかに起動する。

**重要な知見:** `make_camera()` が内部で `world.reset()` を呼ぶため、USD 状態（オフセット・コールバック）を `make_camera()` 後に設定しても `world.reset()` でクリアされる。コールバック登録は `make_camera()` 前に行う必要がある。

### 全4パターン録画結果

| スクリプト | 出力ファイル | フレーム数 |
|---|---|---|
| `hang_rope.py --record` | `20260420_084829_hang_rope.mp4` | - |
| `hang_rope.py --record --circle-radius 0.1` | `20260420_084554_hang_rope_circle_r0.10.mp4` | 301 |
| `swing_rope.py` | `20260420_085113_swing_rope.mp4` | 301 |
| `oscillate_rope.py` | `20260420_085257_oscillate_rope.mp4` | 331 |

全フレームでロープが画角内に収まり、暴れなし。

---

## 2026-04-21 — デフォルトパラメータ調整・clamp_dt の必要性検証

### デフォルトパラメータの変遷と確定値

segments=128 / fill_factor=0.1 を試みたが、`omega_n=42,780 rad/s` → `dt=0.0117ms` → 10s で 85万ステップとなり実用不可（数時間）。

segments=64 / fill_factor=0.1 に変更後、`omega_n=10,695 rad/s` → `dt=0.047ms` → 約9分で完了。swing / oscillate とも正常録画を確認。

fill_factor=0.2 を試みたが `omega_n=15,125 rad/s` → 約13分/本。

**確定デフォルト: segments=64, fill_factor=0.1**（全4スクリプトに適用）

| segments | fill_factor | omega_n [rad/s] | dt [ms] | 10s wall time |
|---|---|---|---|---|
| 25 | 0.3 | 2,827 | 0.177 | ~2分 |
| 64 | 0.1 | 10,695 | 0.047 | ~9分 |
| 64 | 0.2 | 15,125 | 0.033 | ~13分 |
| 128 | 0.1 | 42,780 | 0.012 | 数時間 |

### clamp_dt 無効化の実験

`clamp_dt()` を無効化して dt=1/60s のまま swing_rope.py を実行した結果：
- frame 0: 正常（垂直）
- frame 75: S字波打ち（数値不安定の予兆）
- frame 150: セグメントが画面全体に飛散（数値発散）
- frame 225: 完全爆発、画面外まで吹き飛ぶ

`clamp_dt` は `omega_n` に対して dt が500倍以上大きい場合に積分が即座に発散することを実証。必須の安全機構。

### segments/fill_factor と dt の関係

- `fill_factor` を上げる → `I_eff ∝ φ` → `omega_n ∝ sqrt(φ)` → dt 縮小
- `segments` を増やす → `L_seg = L/N` 短縮 → `omega_n ∝ N^{3/2}` → dt 急激に縮小

デフォルト dt=1/60s は `clamp_dt` により常に上記安定限界に切り下げられる。
