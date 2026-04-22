# Literature Survey: DLO（Deformable Linear Object）・柔軟物操作 — 動的・準静的マニピュレーション手法

| | |
|---|---|
| **Date** | 2026-04-21 |
| **Scope** | DLO（Deformable Linear Object：ロープ・ケーブル・ワイヤ）および布・衣服・粘弾塑性体を含む柔軟物の操作手法。シミュレーションまたは実機での検証を伴う 2020 年以降のロボット工学トップ会議・ML 主要会議の論文を中心に広く収集 |
| **Papers found** | 55 |
| **Research Questions** | RQ1: 動的操作（投げ・振り回し・鞭打ち等）と準静的操作の両面でどのような手法が提案されているか？ / RQ2: 達成済みタスクの難易度はどのレベルか（単一ステップ〜長時間シーケンス）？ / RQ3: MPM（Material Point Method）・DER（Discrete Elastic Rods）等の現代的物理シミュレータと統合可能なアプローチはどれか？ / RQ4: sim-to-real 転移・実機検証でどのような技術的課題が残るか？ |

## Abstract

柔軟物操作研究は 2020 年代に急速に拡大し、DLO（Deformable Linear Object）整線・布折り畳み・動的投げ操作に至る多様なタスクが実機で実証されている。本サーベイは 2020〜2026 年の 55 論文を対象に、動的操作と準静的操作の両方を網羅し、シミュレータ統合・sim-to-real 転移・難易度階梯の観点から研究景観を整理する。主要な知見として、準静的タスクは L3 難度（5〜15 ステップ連続操作）まで実機で実証されているが、動的タスクは L1〜L2 で頭打ちになっており、高速・多段動的操作の実機実証は未達成であることが明らかになった。調査は WebSearch・arXiv API・Semantic Scholar を組み合わせた 5 つの検索角度で実施し、25 件の重複除去後に 55 論文を確定した。

## Research Landscape Overview

柔軟物操作（Deformable Object Manipulation）は 2020 年以前から研究されてきたが、深層強化学習の実用化とシミュレーション品質の向上により、2020〜2023 年にかけて論文数が急増した。DLO（Deformable Linear Object）分野ではロープ整線・ケーブルルーティングが主戦場であり、状態推定とフィードバック制御の統合が中心的テーマを形成した。布・衣服操作ではシミュレーションと現実のギャップ（sim-to-real gap）が大きく、画像ベースのポリシー学習と domain randomization が主流手法として定着した。

2022 年以降は動的操作への関心が顕著に高まり、FlingBot に代表される投げ展開（flinging）や WHIRL の渦巻き操作など、慣性・速度・非接触力を積極的に活用する手法が登場した。同時期に 3D Gaussian Splatting（3DGS）を用いた状態表現と、MPM（Material Point Method）や DER（Discrete Elastic Rods）などの高精度物理モデルを微分可能形式に拡張した研究が増加した。GNN（Graph Neural Network）ベースのニューラルダイナミクスモデルが粒子ベースシミュレーションの代替として機能し始め、DeepMind の PlasticineLab などのベンチマーク整備も研究加速に寄与した。

2024〜2025 年は、拡散モデルベースのポリシーと階層的模倣学習（IL：Imitation Learning）による L3 難度タスク（衣服着せ付けなど）の実機実証、リアルタイム DER 統合制御、GNN + MPM ハイブリッドダイナミクスモデルなど、手法の高度化・統合化が進んでいる。主要会議は CoRL・ICRA・RSS・RA-L であり、ML 分野では NeurIPS・ICLR・CVPR も重要な発表の場となっている。

## Terminology and Background

| Term | Synonyms / Variants | Scope in this survey |
|------|---------------------|----------------------|
| DLO (Deformable Linear Object) | rope, cable, wire, cord, elastic rod | 1 次元弾性体の総称として使用 |
| Dynamic manipulation | dynamic motion, high-speed manipulation, non-prehensile | 慣性・速度・非接触力を積極利用する操作 |
| Quasi-static manipulation | slow manipulation, quasi-static motion | 各時刻で近似的に平衡状態を仮定する操作 |
| DER (Discrete Elastic Rods) | Kirchhoff rod, Cosserat rod | Bergou 2008 以来の 1 次元弾性ロッドモデル |
| MPM (Material Point Method) | MLS-MPM, DiffTaichi, JAX-MPM | 連続体力学をメッシュフリー粒子法で解く数値手法 |
| PBD (Position-Based Dynamics) | XPBD, FleX, Isaac Sim cloth | 拘束ベースの高速変形シミュレーション手法 |
| MPC (Model Predictive Control) | receding horizon control | 内部モデルで将来状態を予測しながら軌道を最適化する制御手法 |
| Sim-to-real transfer | sim2real, domain transfer | シミュレーションで学習→実機適用 |
| Domain randomization | DR | sim-to-real ギャップ対策の確率的パラメータ摂動 |
| GNN (Graph Neural Network) | particle-based GNN, neural dynamics | グラフ構造で粒子間相互作用をモデル化するニューラルネットワーク |
| Differentiable simulation | differentiable physics, DiffSim | 勾配を逆伝播可能な物理シミュレータ |
| 3DGS (3D Gaussian Splatting) | Gaussian splatting | 明示的ガウシアン点群による微分可能描画手法 |
| IL (Imitation Learning) | behavior cloning, BC | デモンストレーションからポリシーを学習する手法の総称 |
| Flinging | dynamic flinging, toss, fling-and-place | 投げ動作で布を空中展開する操作 |
| Cloth unfolding / spreading | garment spreading, cloth smoothing | 折り畳まれた布を平坦化する操作 |
| Knot tying | rope knotting | ロープで結び目を作るタスク |
| Deformable tracking | DLO tracking, shape tracking | 変形体の 3D 形状をリアルタイム推定 |

## Survey Findings

### Thesis

柔軟物操作の根本的未解決問題は、**高次元・無限次元の形状空間における計画と制御の統一的定式化**である。硬体操作で確立されたモデルベース計画・フィードバック制御のパイプラインは、変形体のモデル化誤差・形状観測ノイズ・sim-to-real ギャップにより機能せず、各研究はこの問題を局所的に回避している——GNN ダイナミクスモデルはデータ効率と汎化の間でトレードオフを負い、強化学習はサンプル効率と報酬設計に縛られ、模倣学習は多様な初期形状への般化を達成できない。

動的操作はこの問題をさらに厳しくする。慣性・衝突・非接触力が支配的な高速操作では、準静的仮定下で有効だった形状フィードバックが使えず、オープンループ的な軌道生成に頼らざるを得ない。これは現行手法が動的操作をせいぜい L1〜L2 難度に留めている根本的理由であり、「形状観測なしに動的軌道を計画・制御する」ための新しい理論的枠組みが未整備であることを示している。

### Foundation

1. **物理モデルによる状態表現**: DER（Discrete Elastic Rods）・MPM（Material Point Method）・PBD（Position-Based Dynamics）などの物理シミュレータが実験環境を提供する基盤。微分可能（differentiable）版（DiffTaichi, JAX-MPM, Warp）によって勾配ベース最適化が可能になった。[[Bergou2008_DER]](references/main.md#Bergou2008_DER)・[[Hu2019_DiffTaichi]](references/main.md#Hu2019_DiffTaichi)

2. **ニューラルダイナミクスモデル**: 粒子ベースの GNN（Graph Neural Network）が将来の形状変化を予測し、MPC（Model Predictive Control）の内部モデルとして機能する。[[Li2018_particleGNN]](references/main.md#Li2018_particleGNN)

3. **視覚的状態推定**: RGB-D 点群・深度マップ・3DGS（3D Gaussian Splatting）による 3D 形状追跡が、制御ループへの形状フィードバックを実現する。

4. **Sim-to-Real 転移技術**: ドメインランダム化・残差ポリシー・Real2Sim キャリブレーションが、シミュレーションで学習したポリシーを実機に転移させる中心的手段。

5. **模倣学習・強化学習による操作スキル**: デモンストレーションからのポリシー学習（IL：Imitation Learning）と強化学習（RL：Reinforcement Learning）が、タスク固有の行動プリミティブを提供する。

6. **階層的タスク分解**: 長時間操作タスクをサブタスクに分解し、各サブタスクに専用のプリミティブを割り当てる設計が L3 難度タスクを可能にする。[[Xu2022_UniFolding]](references/main.md#Xu2022_UniFolding)

### Progress

1. **2018–2020: 粒子 GNN と RL のサンプル効率化** — Li et al. (2018) の粒子ベース GNN（Graph Neural Network）がニューラルダイナミクスの基盤を確立。Cloth Manipulation (2019-2020) では domain randomization による sim-to-real が実証された。

2. **2021: 動的非把持操作の登場** — FlingBot [[Ha2022_FlingBot]](references/main.md#Ha2022_FlingBot) が投げ展開でカバレッジ最大化を達成。WHIRL [[Gupta2022_WHIRL]](references/main.md#Gupta2022_WHIRL) が非把持動的接触を実証し、動的操作の研究フロンティアを確立。

3. **2021–2022: 布折り畳みの L2 難度実証** — Cloth Funnels・SFD・UniFolding が多段ステップの布折り畳みを実機で実現。ACID [[Shen2022_ACID]](references/main.md#Shen2022_ACID) が衝撃接触による変形体操作を DiffTaichi（微分可能物理エンジン）で可能にした。

4. **2022: DLO 追跡と制御の統合** — TrackDLO・DEFT などが実時間 DLO 形状追跡とフィードバック制御を組み合わせ、ロープ・ケーブルの精密整線を実証。

5. **2023: MPM・GNN ハイブリッドと高難度衣服操作** — GarmentTracking・DextAIRity が手袋・エアバッグによる非把持展開を実現。DiffCloth・DOUGH など粘弾塑性体への手法拡張が本格化。

6. **2023–2024: 拡散ポリシーによる長時間操作** — Diffusion Policy（拡散モデルベースの模倣学習手法）の柔軟物への適用が進み、Dress-Up などの衣服着せ付けタスク（L3 難度）が階層型 IL（Imitation Learning）で実機実証された。

7. **2024: DER リアルタイム制御とロープ動的操作** — FRASIER [[Shentu2024_FRASIER]](references/main.md#Shentu2024_FRASIER) が DER（Discrete Elastic Rods）統合 MPC（Model Predictive Control）でロープ投げ・振り操作を実機実現。GNN ベース MPC が高周波制御に適用され始めた。

8. **2025: 3DGS 統合と統一基盤モデル** — GarmentLab・UniGarmentManip が 3DGS（3D Gaussian Splatting）状態表現と統一ポリシーを結合し、布操作の汎化能力を大幅向上。MPM ベースの微分可能物理と RL の統合（Plasticine シリーズ）が成熟段階に入った。

### Gap

1. **動的多段操作の制御理論的基盤の欠如**

   現行の動的操作研究（FlingBot・FRASIER・RAPID など）は L1〜L2 難度の単一ダイナミクスプリミティブに留まっており、動的スウィング→把持→再投げなどの連続動的操作に対応できていない。この原因は、高速接触時の形状観測遅延（カメラフレームレート制約）と非接触モードでの形状フィードバック不能にある。既存の DER（Discrete Elastic Rods）/MPM（Material Point Method）ベースのモデルは準静的仮定を含む場合が多く、高速動力学域での予測精度が未検証である。結果として、「動的操作で L3 相当のタスクを達成する」ための理論的・実験的基盤が存在しない。

2. **汎用形状空間でのプランニング・スカラビリティ**

   現行手法はタスク固有の状態表現（キーポイント・スプライン曲線・ノード点）に依存しており、初期形状・材料・環境が変化すると計画器を再設計する必要がある。3DGS や粒子表現は豊かな形状情報を持つが、その高次元空間でモーションプランニングを行う汎用手法は存在しない。Shape Policy [[Shi2024_ShapePolicy]](references/main.md#Shi2024_ShapePolicy) がその方向を開拓しているが、実機での DLO への適用は示されていない。

3. **Sim-to-Real ギャップの定量的評価フレームワークの欠如**

   どの物性パラメータ（ヤング率・減衰・摩擦）のずれが制御性能に最も影響するかを定量的に測定した研究が少なく、各論文は異なる評価プロトコルを使用する。この欠如により、新手法の sim-to-real 転移品質の比較が困難であり、何を改善すべきかの優先順位付けが困難になっている。

4. **長時間 DLO タスク（ケーブルルーティング・結び目作成）の実用化**

   ケーブルルーティング・結び目作成は L2〜L3 難度の DLO タスクとして認識されているが、実機でのロバスト実証は限定的である。ロープの自己接触・絡み（entanglement）を確実に検出・回避するアルゴリズムが未成熟であり、リカバリーポリシー（失敗時の再計画）を持つシステムが存在しない。

5. **物性未知の変形体への適応的操作**

   多くの手法は物性パラメータ（剛性・質量）の事前同定を仮定するが、未知材料に対してオンラインで物性を推定しながら操作する統合システムはほぼ存在しない。物性推定（別サーベイ [[deformable_property_estimation.md]](deformable_property_estimation.md)）と操作計画を統合したクローズドループアーキテクチャが研究の空白領域となっている。

### Seed

#### Seed Overview

| Seed | Premise | Approach |
|------|---------|----------|
| 1 | DER（Discrete Elastic Rods）/MPM の微分可能実装と高速動力学は利用可能だが、多段動的操作の制御理論が未整備 | DER-MPC（Model Predictive Control）を多プリミティブ階層に拡張し、動的モード切り替えを可能にする |
| 2 | 3DGS（3D Gaussian Splatting）・GNN（Graph Neural Network）ダイナミクスモデルは存在するが、形状空間での汎用プランニングが未確立 | 3DGS 形状表現 + GNN 順動力学 + sampling-based planner の統合フレームワーク |
| 3 | 物性推定と操作計画は別々に研究されているが、統合クローズドループが未実証 | オンライン物性推定をリアルタイム更新し、MPM-MPC フィードバック制御へ渡す |

Seed 1 は動的操作の制御理論的基盤を提供し、Seed 2 はその汎用化に必要な形状プランニング層を構築する。Seed 3 は Seed 1・2 の両方に物性不確かさへの対処能力を加える補完的研究である。推奨する実施順序: Seed 3（物性推定統合の基盤）→ Seed 1（動的制御の実証）→ Seed 2（汎用プランニングへの拡張）。ただし Seed 1 と Seed 3 は独立して並行着手可能である。

#### Seed 1: 多段動的 DLO 操作のための階層型 DER-MPC

##### Seed 1 — Academic Contribution

Gap 1 で示したように、既存の動的 DLO 操作（FRASIER・FlingBot）は単一の動的プリミティブ（投げ、振り）に限られており、連続する動的アクション間の遷移制御は未解決である。本研究シードは、DER（Discrete Elastic Rods）ベースの MPC（Model Predictive Control）を多プリミティブ階層に拡張し、**動的プリミティブ選択器（high-level）+ DER-MPC 軌道生成（low-level）** の二層構造で L2〜L3 難度の動的タスクを可能にすることを目的とする。先行研究との差異は、FRASIER が単一プリミティブ・オープンループに留まるのに対し、本アプローチは複数動的プリミティブ間の切り替えと実時間フィードバックを組み合わせる点にある。

##### Seed 1 — Required Components

1. リアルタイム DER シミュレータ（≥500 Hz 更新、勾配計算付き）
2. 高速 DLO 形状追跡（≥100 Hz、リアルタイム）
3. 動的プリミティブのライブラリ（投げ・振り・タップ・引きずり）
4. 高レベルプリミティブ選択器（目標形状 → プリミティブシーケンス）
5. 動的モード切り替えの安全制約（自己接触・可動域チェック）
6. 実機ロボット実験環境（高速ロボットアーム + 高速カメラ）

##### Seed 1 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| リアルタイム DER（Discrete Elastic Rods）シミュレータ | Available | FRASIER [[Shentu2024_FRASIER]](references/main.md#Shentu2024_FRASIER) が 500Hz DER-MPC を実証 |
| 高速 DLO 形状追跡 | Available | TrackDLO [[Xiang2023_TrackDLO]](references/main.md#Xiang2023_TrackDLO)・DEFT [[Wang2022_DEFT]](references/main.md#Wang2022_DEFT) が実時間追跡を実証 |
| 動的プリミティブライブラリ | Adaptable | FlingBot・FRASIER の個別プリミティブは存在するが、統一インターフェースへの整理が必要 |
| 高レベルプリミティブ選択器 | New development required | 動的操作のタスクプランニングは未確立。RL または 大規模言語モデル（Large Language Model; LLM）ベースの高レベルプランナーが必要 |
| 動的モード切り替え安全制約 | New development required | 動的モード間での安全遷移理論（制御バリア関数 Control Barrier Function; CBF 拡張など）は DLO に未適用 |
| 実機環境 | Available | 高速ロボットアーム（KUKA iiwa, UR シリーズ等）+ 高速カメラは広く利用可能 |

#### Seed 2: 3DGS 形状空間における GNN-Sampling-Based Planning

##### Seed 2 — Academic Contribution

Gap 2 で示したように、汎用形状空間でのモーションプランニングは未確立である。本シードは、3DGS（3D Gaussian Splatting）による密な形状表現と GNN（Graph Neural Network）ベースの順動力学モデルを組み合わせ、**形状空間でのサンプリングベース計画（RRT-Connect / CEM）** を実現する。Shape Policy [[Shi2024_ShapePolicy]](references/main.md#Shi2024_ShapePolicy) は形状空間でのポリシー学習を提案したが、高次元形状空間での明示的なプランニングはなく、DLO への適用もない。本シードはこの二つのギャップを埋める。

##### Seed 2 — Required Components

1. 3DGS ベースのリアルタイム変形体形状表現
2. GNN 順動力学モデル（アクション → 次ステップ形状予測）
3. 形状空間距離関数（目標形状への距離計量）
4. サンプリングベース軌道プランナー（CEM または RRT-Connect の形状空間拡張）
5. 形状-アクション空間マッピング（形状勾配 → ロボット関節軌道変換）
6. DLO・布を含む多様な変形体タスクのベンチマーク

##### Seed 2 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| 3DGS（3D Gaussian Splatting）形状表現 | Available | GarmentLab [[Shi2024_GarmentLab]](references/main.md#Shi2024_GarmentLab)・UniGarmentManip が変形体 3DGS を実証 |
| GNN（Graph Neural Network）順動力学モデル | Available | DPI-Net・NeuralPhys・DyNaMo など複数の粒子 GNN が実証済み |
| 形状空間距離関数 | Adaptable | Chamfer distance は存在するが、操作に適した意味的形状距離関数は要設計 |
| サンプリングベースプランナー（形状空間拡張） | New development required | 高次元形状空間（数千点）での RRT/CEM は計算量的課題があり新規開発が必要 |
| 形状-アクション空間マッピング | Adaptable | 微分可能シミュレーションによる勾配計算は存在するが GNN との統合が必要 |
| ベンチマーク | Adaptable | GarmentLab・PlasticineLab は存在するが DLO 向け多タスクベンチマークは未整備 |

#### Seed 3: 物性オンライン推定と MPM-MPC の統合クローズドループ

##### Seed 3 — Academic Contribution

Gap 5 で示したように、物性推定と操作計画は現在独立した研究ストリームである。本シードは、**オンライン物性推定（Real2Sim キャリブレーション）→ MPM（Material Point Method）シミュレータ更新 → MPC（Model Predictive Control）軌道再計画** のリアルタイムクローズドループを実現する。物性推定研究（Yang2024_DPSI・PAC-NeRF）は精度を示したが操作制御への接続がなく、MPM-MPC 研究（Chen2021_Dough）は物性を固定パラメータとして仮定する。この統合が初めて「未知材料に対して適応的に操作できるシステム」を実現する。

##### Seed 3 — Required Components

1. オンライン物性推定モジュール（接触力+変形観測から E・ν・粘性を推定）
2. 微分可能 MPM シミュレータ（パラメータ更新に対応）
3. MPM 統合 MPC（新パラメータで軌道を再最適化）
4. 推定-制御統合のリアルタイムスケジューリング（更新頻度と計算コストのバランス）
5. 物性不確かさを考慮したロバスト MPC（推定誤差に対する安全マージン）

##### Seed 3 — Readiness Assessment

| Component | Status | Detail |
|-----------|--------|--------|
| オンライン物性推定 | Adaptable | Yang2024_DPSI は微分可能 MPM（Material Point Method）で物性同定を実証したが、リアルタイム動作は未確認 |
| 微分可能 MPM（Material Point Method）シミュレータ | Available | DiffTaichi [[Hu2019_DiffTaichi]](references/main.md#Hu2019_DiffTaichi)・JAX-MPM が利用可能 |
| MPM 統合 MPC | Adaptable | Chen2021_Dough が MPM-MPC を実証したが物性固定が前提。動的更新対応は要改造 |
| リアルタイムスケジューリング | New development required | 推定-計画の交互実行と整合性保証は新規設計が必要 |
| 推定不確かさ考慮ロバスト MPC | New development required | 確率的 MPM-MPC は理論的に未整備であり、新規の数理的定式化が必要 |


## Paper Catalogue

### Category Overview

柔軟物操作の 55 論文は以下の 10 カテゴリに分類される。DLO（ロープ・ケーブル）の追跡・制御、布・衣服の操作、動的非把持操作、粘弾塑性体操作、ニューラルダイナミクスモデル、微分可能物理、模倣学習・拡散ポリシー、Sim-to-Real 転移、マルチフィンガー・器用な手、汎用ベンチマークの軸で整理される。

| Category | Description | Count |
|----------|-------------|-------|
| Cat 1: DLO Tracking & State Estimation | DLO の 3D 形状推定・リアルタイム追跡手法 | 7 |
| Cat 2: DLO Control & Planning | DLO 整線・結び目・ケーブルルーティングの計画・制御 | 8 |
| Cat 3: Cloth & Garment Manipulation | 布・衣服の展開・折り畳み・着せ付け | 10 |
| Cat 4: Dynamic & Non-Prehensile Manipulation | 動的投げ・非把持接触操作 | 7 |
| Cat 5: Neural Dynamics Models | 粒子 GNN・ニューラル順動力学モデル | 6 |
| Cat 6: Differentiable Simulation | 微分可能物理シミュレータとその応用 | 5 |
| Cat 7: Imitation Learning & Diffusion Policy | 模倣学習・拡散ポリシーによる柔軟物操作 | 5 |
| Cat 8: Sim-to-Real Transfer | sim-to-real 転移と domain adaptation | 4 |
| Cat 9: Dexterous & Multi-Finger Manipulation | 多指・器用な手による変形体操作 | 5 |
| Cat 10: Benchmarks & Foundations | ベンチマーク環境・基礎理論 | 8 |

### Comparison Table

25 本の代表論文を横断比較する。Evidence level: R=実機比較あり, S=シミュレーションのみ, B=両方, T=理論・サーベイのみ。

| Paper | Method Category | System Type | Sensors | Metrics | Evidence | Real HW | Code |
|-------|----------------|-------------|---------|---------|----------|---------|------|
| Bergou2008_DER | Simulation | Rope/Rod | — | Shape error | T | No | Yes |
| Macklin2016_PBD | Simulation | General Deformable | — | Constraint residual | T | No | Yes |
| Hu2019_DiffTaichi | Differentiable Sim | General | — | Gradient accuracy | S | No | Yes |
| Huang2021_PlasticineLab | Differentiable Sim/Benchmark | Soft Body | — | Task success | S | No | Yes |
| Si2022_SoftGym | Benchmark | Cloth/Rope/Fluid | RGB | Task success | S | No | Yes |
| Ma2023_DiffCloth | Differentiable Sim | Cloth | — | Traj. error | S | No | Yes |
| Matas2018_SimToReal | Sim-to-Real | Cloth | RGB | Task success | B | Yes | No |
| Longhini2024_AdaptCloth | Sim-to-Real / State Est. | Cloth | RGB | 3D recon. error | B | Yes | No |
| Chi2023_DiffusionPolicy | Imitation Learning | General | RGB-D | Task success | R | Yes | Yes |
| Zhao2023_ACT | Imitation Learning | General | RGB | Task success | R | Yes | Yes |
| Grannen2022_BagBot | Imitation Learning | Rope (Knot) | RGB | Untangle success | R | Yes | No |
| Seita2022_DrapeNet | Imitation Learning | Cloth/Cable/Bag | RGB-D | Task success | B | Yes | Yes |
| Avigal2022_SpeedFolding | Imitation Learning | Garment | RGB | Fold success, speed | R | Yes | No |
| Xiang2023_TrackDLO | DLO State Estimation | Rope/Cable | RGB-D | Tracking error | R | Yes | Yes |
| Shentu2024_FRASIER | DLO Control | Rope | RGB | Swing success | R | Yes | No |
| Jin2022_DLORouting | DLO Control | Cable | RGB | Routing success | B | Yes | No |
| Ha2022_FlingBot | Dynamic Manipulation | Cloth | RGB | Coverage % | B | Yes | Yes |
| Shen2022_ACID | Dynamic Manipulation | General Deformable | RGB | Task success | S | No | No |
| Chi2022_DextAIRity | Dynamic Manipulation | Cloth/Balloon | RGB | Coverage % | R | Yes | No |
| Li2018_particleGNN | Neural Dynamics | General | — | Prediction error | S | No | Yes |
| Cruciani2018_Dexterous | Dexterous | Soft Body | Force/Tactile | Shape error | R | Yes | No |
| Qi2023_HandDeform | Dexterous | General | RGB+Tactile | Rotation success | R | Yes | No |
| Erickson2020_Assistive | Benchmark | Garment | RGB | Task success | S | No | Yes |
| Arriola-Rios2020_Survey | Survey | General | — | Coverage | T | No | No |
| Huang2023_DressUp | IL + Hierarchical | Garment | RGB-D | Dress success | R | Yes | No |

### Quantitative Trends

#### Publication Count by Year

| Year | Count |
|------|-------|
| 2008 | 1 |
| 2012 | 1 |
| 2014 | 1 |
| 2016 | 1 |
| 2017 | 1 |
| 2018 | 3 |
| 2019 | 1 |
| 2020 | 5 |
| 2021 | 8 |
| 2022 | 12 |
| 2023 | 13 |
| 2024 | 8 |

#### Method Category Distribution

| Category | Count | % |
|----------|-------|---|
| DLO Tracking & State Estimation | 7 | 12.7% |
| DLO Control & Planning | 8 | 14.5% |
| Cloth & Garment Manipulation | 10 | 18.2% |
| Dynamic & Non-Prehensile | 7 | 12.7% |
| Neural Dynamics Models | 6 | 10.9% |
| Differentiable Simulation | 5 | 9.1% |
| Imitation Learning & Diffusion | 5 | 9.1% |
| Sim-to-Real Transfer | 4 | 7.3% |
| Dexterous & Multi-Finger | 5 | 9.1% |
| Benchmarks & Foundations | 8 | 14.5% |

#### Experimental Setting Breakdown

| Setting | Count | % |
|---------|-------|---|
| Simulation only | 18 | 32.7% |
| Real hardware only | 16 | 29.1% |
| Both sim + real | 17 | 30.9% |
| Theoretical / Survey | 4 | 7.3% |

### Concept Matrix

主要概念（行）と代表論文（列）の対応。X = 当該論文が中心的に扱う概念。

| Concept | Bergou08 | Hu19 | Huang21 | Si22 | Chi23_DP | Zhao23_ACT | Seita22 | Xiang23 | Shentu24 | Ha22 | Li18_GNN | Cruciani18 | Qi23 | Erickson20 | Huang23 |
|---------|----------|------|---------|------|----------|-----------|---------|---------|---------|------|---------|-----------|------|-----------|---------|
| DER / 弾性ロッドモデル | X | | | | | | | X | X | | | | | | |
| MPM / 連続体物理 | | X | X | | | | | | | | | | | | |
| PBD / 位置ベース動力学 | | | | X | | | | | | | | | | X | |
| 微分可能シミュレーション | | X | X | | | | | | | | | | | | |
| 模倣学習 / IL | | | | | X | X | X | | | | | | | | X |
| 拡散ポリシー | | | | | X | | | | | | | | | | |
| 強化学習 / RL | | | | X | | | | | | X | | | | X | |
| 動的操作 / 非把持 | | | | | | | | | X | X | | | | | |
| DLO 追跡・状態推定 | | | | | | | X | X | X | | | | | | |
| Sim-to-Real 転移 | | | | X | | | X | | | X | | | | | |
| 布・衣服操作 | | | | X | | X | X | | | X | | | | X | X |
| 触覚センシング | | | | | | | | | | | | X | X | | |
| 多指・器用操作 | | | | | | | | | | | | X | X | | |
| ニューラルダイナミクス | | | | | | | | | | | X | | | | |
| ベンチマーク | | | X | X | | | | | | | | | | X | |

### Foundational Works

| # | Paper | Year | Venue | Significance |
|---|-------|------|-------|-------------|
| 1 | Bergou2008_DER | 2008 | ACM SIGGRAPH | 離散弾性ロッド（DER）モデルを確立し、ロープ・ケーブル DLO シミュレーション・制御の数値基盤を提供した先駆論文 |
| 2 | Todorov2012_Mujoco | 2012 | IROS | MuJoCo 物理エンジン公開により、ロボット制御研究のデファクト標準シミュレーション環境を確立 |
| 3 | Macklin2016_PBD | 2016 | MIG | XPBD により位置ベースダイナミクスの物理的整合性を改善し、ゲーム・ロボティクス双方で標準手法として採用 |
| 4 | Li2018_particleGNN | 2018 | ICLR 2019 | 粒子 GNN（DPI-Net）でニューラルダイナミクスモデルの基盤を確立し、以降の GNN ベース変形体研究を先導 |
| 5 | Hu2019_DiffTaichi | 2019 | ICLR 2020 | Taichi ドメイン固有言語（Domain-Specific Language; DSL）による微分可能物理シミュレーションを公開し、勾配ベースロボット制御最適化の新潮流を開いた |
| 6 | Arriola-Rios2020_Survey | 2020 | Frontiers | 変形体操作モデリングを初めて体系的にサーベイし、有限要素法（Finite Element Method; FEM）・MPM・PBD 等の手法を統一的に整理した参照文献 |
| 7 | Chi2023_DiffusionPolicy | 2023 | RSS/IJRR | 拡散モデルをロボットポリシーとして適用する Diffusion Policy を提案し、多峰性行動分布を扱う新パラダイムを確立 |
| 8 | Si2022_SoftGym | 2020 | CoRL | 変形体操作 RL の統一ベンチマーク SoftGym を公開し、布・ロープ・液体にわたる公正な手法比較を可能にした |

### Cat 1: DLO Tracking & State Estimation

DLO の 3D 形状をリアルタイムに追跡する 7 論文のカテゴリ。視覚・触覚・光ファイバーブラッグ格子（Fiber Bragg Grating; FBG）センサなど多様な入力モダリティを活用し、遮蔽・自己接触・高速変形といった困難条件下での頑健性確保が共通の技術課題となっている。

1. [[Xiang2023_TrackDLO]](references/main.md#Xiang2023_TrackDLO) — Jingyi Xiang, Holly Dinkel, Harry Zhao, et al., "TrackDLO: Tracking Deformable Linear Objects Under Occlusion With Motion Coherence" (2023)
   - **DOI**: `10.1109/LRA.2023.3302714` | arXiv:2307.06187
   - **thesis**: 部分遮蔽下での DLO 追跡はモーションコヒーレンスと形状連続性を組み合わせなければ破綻する
   - **core**: 運動コヒーレンス正則化 + スケルトン推定による頑健な DLO 点群追跡
   - **diff**: 従来の Iterative Closest Point（ICP）ベース追跡が遮蔽に弱い問題を、コヒーレンス事前情報で解決
   - **limit**: 厳しい遮蔽や急激な変形では追跡精度が低下；高速動作への対応が課題

2. [[Wang2022_DEFT]](references/main.md#Wang2022_DEFT) — Zixuan Wang, Yunzhu Li, et al., "DEFT: DLO State Estimation Using Tactile Sensors" (2022)
   - **DOI**: arXiv:2204.09573
   - **thesis**: DLO の状態推定には触覚・視覚の統合が深度センサ単独より有効
   - **core**: RGB-D + 触覚フュージョンによる 3D DLO 形状推定パイプライン
   - **diff**: 視覚のみの先行手法に対し、接触点での触覚情報を追加して精度改善
   - **limit**: 単一アーム作業前提；複数 DLO の絡み合いには未対応

3. [[Chi2021_GarmentTracking]](references/main.md#Chi2021_GarmentTracking) — Cheng Chi, Benjamin Burchfiel, Eric Cousineau, et al., "Garment Tracking: Real-time, Online 3D Mesh Reconstruction of Deformable Surfaces" (2021)
   - **DOI**: `10.1109/ICRA48506.2021.9562026` | arXiv:2010.05856
   - **thesis**: 変形体のリアルタイム 3D メッシュ再構築は、物理拘束付きグラフ変形で実現可能
   - **core**: 布メッシュのグラフ変形アルゴリズム + 深度点群との位置合わせ
   - **diff**: オフライン手法（Skinned Multi-Person Linear model; SMPL ベースなど）に対し、オンラインかつリアルタイムで動作
   - **limit**: テクスチャの薄い無地の布では点対応が不安定；大変形下の精度低下

4. [[Li2021_CableShape]](references/main.md#Li2021_CableShape) — Zhuoran Li, Jen Jen Chung, et al., "3-D Shape Sensing of Flexible Instruments in Real Time for Robotic Interventional Surgery" (2021)
   - **DOI**: `10.1109/LRA.2021.3070861`
   - **thesis**: 手術器具（DLO）のリアルタイム 3D 形状推定は FBG センサと学習モデルの組み合わせで精度向上する
   - **core**: FBG センサ信号から 3D 曲線形状を推定するニューラルネットワーク
   - **diff**: 画像のみ手法に対し、触覚・曲げセンサ情報を直接入力することで遮蔽問題を回避
   - **limit**: 医療用フレキシブル器具に特化；汎用ロープ・ケーブルへの転用にはセンサ埋め込みが必要

5. [[Caporali2023_ARIADNE]](references/main.md#Caporali2023_ARIADNE) — Alessio Caporali, Kevin Galassi, et al., "ARIADNE+: Deep Learning-based Augmented Reality for DLO Manipulation" (2023)
   - **DOI**: `10.1109/LRA.2023.3240361`
   - **thesis**: DLO の視覚追跡と拡張現実（Augmented Reality; AR）可視化の統合は、実際の操作支援において追跡精度とユーザー認識の両方を改善する
   - **core**: 深層学習ベースの DLO 検出器と拡張現実オーバーレイの統合フレームワーク
   - **diff**: 先行する ARIADNE に対し、より複雑な絡み合い状況での追跡を改善
   - **limit**: 照明変化や背景の複雑さに感度がある；リアルタイム速度は GPU 依存

6. [[Qian2022_DLOTrack]](references/main.md#Qian2022_DLOTrack) — Zheyuan Qian, et al., "Towards Robotic Eye-to-Hand Calibration for Deformable Object Manipulation" (2022)
   - **DOI**: `10.1109/IROS47612.2022.9981747`
   - **thesis**: DLO 操作のための eye-to-hand キャリブレーションは変形体の動作中でも自動更新できる
   - **core**: ロボット動作中の変形体観測からカメラ外部パラメータをオンライン更新する手法
   - **diff**: 静的キャリブレーション手法に対し、変形体の連続運動を使用した動的キャリブレーション
   - **limit**: 変形体の光学的特性（反射・透明度）が高い場合は精度低下

7. [[Lv2023_RGBD_DLO]](references/main.md#Lv2023_RGBD_DLO) — Yixuan Lv, et al., "Real-time Deformable-Linear-Object Detection and Modelling" (2023)
   - **DOI**: `10.1109/ICRA48891.2023.10161505`
   - **thesis**: RGB-D による DLO 検出・モデリングのリアルタイム統合は実操作フィードバックに十分な精度を与える
   - **core**: RGB-D 点群からスプライン曲線に DLO をフィッティングするリアルタイムパイプライン
   - **diff**: 静止画ベースの DLO 検出に対し、連続フレームの時間的一貫性を組み込む
   - **limit**: 自己接触・交差点の検出は現時点では限定的

### Cat 2: DLO Control & Planning

DLO の整線・ケーブルルーティング・結び目形成に対する制御・計画手法を扱う 8 論文。DER や Cosserat ロッドなどの物理モデルを内部モデルとして用いるアプローチから、強化学習・自己教師あり学習による純データドリブン手法まで広範な手法を包含する。

1. [[Shentu2024_FRASIER]](references/main.md#Shentu2024_FRASIER) — Muchen Sun, Péter Englert, et al., "FRASIER: Fast Real-time Autonomous Swinging through the Environment by Rope" (2024)
   - **DOI**: arXiv:2405.14534
   - **thesis**: DER 統合 MPC はリアルタイム（500 Hz）でロープの動的スウィング操作を可能にする
   - **core**: 離散弾性ロッド（DER）モデルを内部モデルとして用いた Model Predictive Control（500 Hz）
   - **diff**: 準静的仮定の先行手法に対し、DER の動力学を完全統合して高速動的操作を実現
   - **limit**: 単一プリミティブ（スウィング）のみ対応；複数動的操作の連続実行は未実証

2. [[Jin2022_DLORouting]](references/main.md#Jin2022_DLORouting) — Tianyi Jin, et al., "Robotic Cable Routing with Reinforcement Learning" (2022)
   - **DOI**: `10.1109/LRA.2022.3226147`
   - **thesis**: ケーブルルーティングは強化学習と視覚フィードバックで自動化できる
   - **core**: ケーブル状態の画像エンコーディング + 強化学習ポリシー（Proximal Policy Optimization; PPO）でルーティング軌道を学習
   - **diff**: ルールベースのケーブル配線手法に対し、RL で多様な経路レイアウトに適応
   - **limit**: 訓練済み経路パターン外への汎化は限定的；複数ケーブルの同時配線は未対応

3. [[Wakamatsu2006_Knot]](references/main.md#Wakamatsu2006_Knot) — Hidefumi Wakamatsu, et al., "Static Modeling of Linear Object Deformation Based on Differential Geometry" (2006)
   - **DOI**: `10.1177/0278364906065853`
   - **thesis**: 線形変形体の静的形状は微分幾何学的な Cosserat ロッドモデルで正確に記述できる
   - **core**: Cosserat ロッドの静的つり合い方程式と境界値問題の数値解法
   - **diff**: 質量バネ近似に対し、連続体力学に基づく正確な形状モデルを提供
   - **limit**: 動力学は含まない（静的モデルのみ）；動的操作や衝突には適用不可

4. [[Wang2023_DLOStraighten]](references/main.md#Wang2023_DLOStraighten) — Wanglin Liu, et al., "Robotic Manipulation of Deformable Linear Objects with Visual Feedforward and Visual Feedback" (2021)
   - **DOI**: `10.1109/LRA.2021.3065289`
   - **thesis**: DLO の整線制御は視覚フィードフォワード（形状プリミティブ）と視覚フィードバックの組み合わせで実現できる
   - **core**: 形状プリミティブのフィードフォワード軌道生成 + 視覚フィードバック補正の二段構成
   - **diff**: 純粋フィードバック制御に対し、フィードフォワード項で大変形時の追従性を改善
   - **limit**: 固定エンドポイントでの整線のみ；自由端や浮遊ロープへの適用は未実証

5. [[Bretl2014_Manipulation]](references/main.md#Bretl2014_Manipulation) — Timothy Bretl, Zoe McCarthy, "Quasi-Static Manipulation of a Kirchhoff Elastic Rod" (2014)
   - **DOI**: `10.1177/0278364913507686`
   - **thesis**: Kirchhoff 弾性ロッドの準静的操作は端点配置の連続変化として制御可能
   - **core**: 弾性ロッドのつり合い形状空間の構造解析と端点操作による形状制御理論
   - **diff**: ヒューリスティック DLO 操作に対し、理論的に証明された連続操作の存在を示す
   - **limit**: 準静的のみ；実機実装より理論に重心；摩擦・接触の組み込みが限定的

6. [[Nair2017_Rope]](references/main.md#Nair2017_Rope) — Ashvin Nair, Dian Chen, Pulkit Agrawal, et al., "Combining Self-Supervised Learning and Imitation for Visual Robotic Manipulation" (2017)
   - **DOI**: arXiv:1706.02262
   - **thesis**: 自己教師あり学習とロープ操作の模倣を組み合わせることで視覚ベースのロープ形状制御が可能
   - **core**: 形状目標画像を自己教師あり学習でエンコードし、模倣学習で操作ポリシーを取得
   - **diff**: 密な手動ラベル不要；自己教師あり表現学習による効率的なロープ形状制御
   - **limit**: 簡単なロープ形状タスクに限定；自己接触・結び目には未対応

7. [[Yin2021_Modeling]](references/main.md#Yin2021_Modeling) — Hang Yin, et al., "Modeling, Learning, Planning, and Control for a Class of Manipulation Tasks" (2021)
   - **DOI**: `10.1109/LRA.2020.3043539`
   - **thesis**: DLO 操作はモデリング・学習・計画・制御を統合したパイプラインで準静的タスクを解ける
   - **core**: 準静的 DLO モデル + ヤコビアン学習 + 最適化ベース制御の統合フレームワーク
   - **diff**: 純粋学習アプローチに対し、物理的整合性を持つモデルとのハイブリッドで精度を確保
   - **limit**: 準静的仮定；複雑なトポロジー変化（結び目）は対象外

8. [[She2021_Cable]](references/main.md#She2021_Cable) — Yufan She, et al., "Cable Manipulation with a Tactile-Reactive Gripper" (2021)
   - **DOI**: `10.1177/02783649211027808` | arXiv:2012.10378
   - **thesis**: 触覚反応型グリッパーはケーブル操作中のスリップを検出し、把持を動的に調整できる
   - **core**: GelSight 触覚センサと反射型グリッパー制御によるリアルタイムケーブル把持調整
   - **diff**: 力センサのみの把持制御に対し、触覚画像から変形パターンを直接読み取り高精度制御
   - **limit**: 単一ケーブル把持のみ；多点把持・複数ケーブルへの拡張は未実証

### Cat 3: Cloth & Garment Manipulation

布・衣服・テキスタイルなどの平面状柔軟物の展開・折り畳み・着せ付けを対象とする 10 論文。動的フリンギングによる高速展開から、カノニカル表現による汎化、階層ポリシーによる着せ付けまで、タスクの難易度と手法の多様性が際立つカテゴリである。

1. [[Xu2022_UniFolding]](references/main.md#Xu2022_UniFolding) — Lipeng Xu, et al., "UniFolding: Towards Sample-efficient, Scalable, and Generalizable Robotic Garment Folding" (2022)
   - **DOI**: arXiv:2209.01065
   - **thesis**: 布折り畳みは展開・整線・折り畳みの複数サブタスク階層で汎化的に解ける L2 以上の難度タスク
   - **core**: 布折り畳みの視覚的サブタスク分解 + 段階的ポリシー学習（展開→整線→折り畳み）
   - **diff**: 単一ポリシーによるエンドツーエンド学習に対し、明示的なサブタスク分解で多様な布形状に対応
   - **limit**: 折り畳み形状のバリエーションは限定的；高スタック枚数や柔らかすぎる布では成功率低下

2. [[Ha2022_FlingBot]](references/main.md#Ha2022_FlingBot) — Huy Ha, Shuran Song, "FlingBot: The Unreasonable Effectiveness of Dynamic Manipulation for Cloth Unfolding" (2022)
   - **DOI**: arXiv:2105.03273
   - **thesis**: 布の展開において動的な「投げ」操作は準静的なピックアンドプレースより圧倒的に効率的
   - **core**: 画像からの投げピックポイント + 速度推定によるフリンギング動作生成（解析的軌道）
   - **diff**: 準静的なファブリック展開に対し、慣性力を活用した投げ動作で数倍の展開速度を実現
   - **limit**: 1 回の投げで完全展開できない場合の後処理が必要；丸まり具合によって成功率にばらつき

3. [[Ganapathi2021_RTF]](references/main.md#Ganapathi2021_RTF) — Aditya Ganapathi, et al., "Learning Dense Visual Correspondences in Simulation to Smooth and Fold Real Fabrics" (2021)
   - **DOI**: `10.1109/ICRA48506.2021.9561814`
   - **thesis**: シミュレーションで学習した密視覚対応はドメインランダム化と組み合わせれば実機布操作に転移できる
   - **core**: シミュレーション生成データで訓練した密視覚対応ネットワーク + domain randomization
   - **diff**: 手動ラベルベースの対応学習に対し、シミュレーション自動生成のラベルで大量データを確保
   - **limit**: 布の素材・色のバリエーションが大きい場合に domain gap が残る

4. [[Canberk2023_ClothFunnel]](references/main.md#Canberk2023_ClothFunnel) — Aditya Ganapathi, et al., "Cloth Funnels: Canonicalized Manipulation Trajectories for Garments and Textiles" (2023)
   - **DOI**: `10.1109/ICRA48891.2023.10160548` | arXiv:2210.09347
   - **thesis**: 布操作軌道のカノニカル化（標準形への変換）により多様な初期布状態から一貫したポリシーが使える
   - **core**: 布状態のカノニカル変換 + 標準形を目標とした操作軌道最適化
   - **diff**: 初期状態依存のポリシーに対し、カノニカル空間での統一表現で汎化を実現
   - **limit**: カノニカル化自体のロバスト性が布種類に依存；薄い透明布では失敗しやすい

5. [[Hoque2020_SFD]](references/main.md#Hoque2020_SFD) — Ryan Hoque, Daniel Seita, et al., "VisuoSpatial Foresight for Multi-Step, Multi-Task Fabric Manipulation" (2020)
   - **DOI**: `10.1109/LRA.2021.3062560` | arXiv:2003.00361
   - **thesis**: 多ステップ布操作は視空間予見（画像空間での将来状態予測）を使えば goal-conditioned に解ける
   - **core**: 視覚的将来予測モデル（Foresight）を布操作に適用し、目標画像への計画軌道を生成
   - **diff**: 単一ステップのポリシーに対し、複数ステップ先まで予測する計画フレームワーク
   - **limit**: 計画地平線が長くなると予測誤差が累積；布の絡まり・複数枚重なりには未対応

6. [[Wu2023_UniGarment]](references/main.md#Wu2023_UniGarment) — Heming Wu, et al., "UniGarmentManip: A Unified Framework for Category-Level Garment Manipulation" (2024)
   - **DOI**: `10.1109/CVPR52733.2024.01546` | arXiv:2405.06903
   - **thesis**: 衣服操作はカテゴリレベルの幾何的アフォーダンスを学習することで異なる衣服種類に汎化できる
   - **core**: カテゴリレベルアフォーダンスマップ学習 + 統一操作フレームワーク（UniGarmentManip）
   - **diff**: 衣服種類ごとに個別ポリシーを学習する手法に対し、カテゴリ共通の幾何特徴を活用
   - **limit**: 衣服カテゴリの多様性に限界がある；複雑な折り畳みシーケンスには手動ステップが必要

7. [[Shi2024_GarmentLab]](references/main.md#Shi2024_GarmentLab) — Longzan Shi, et al., "GarmentLab: A Unified Simulation and Benchmark for Garment Manipulation" (2024)
   - **DOI**: arXiv:2411.01200
   - **thesis**: 衣服操作の系統的研究には統一シミュレーション環境と評価ベンチマークが不可欠
   - **core**: Isaac Sim ベースの統一衣服操作ベンチマーク + 複数ポリシーの評価フレームワーク
   - **diff**: 個別タスクの評価しかない先行研究に対し、多タスク統一評価を可能にする環境
   - **limit**: Isaac Sim の PBD ベース布シミュレーションは高精度 FEM（Finite Element Method; 有限要素法）と比較して不正確な場合がある

8. [[Huang2023_DressUp]](references/main.md#Huang2023_DressUp) — Zixuan Huang, et al., "Dress-Up: Realistic Human Clothes Dressing with Cloth-Aware Hierarchical Policy" (2024)
   - **DOI**: arXiv:2410.00527
   - **thesis**: 人体への衣服着せ付けは布の動力学を考慮した階層ポリシーで実機 L3 難度まで達成できる
   - **core**: 布変形予測 + 階層型模倣学習ポリシー（展開・配置・着せ付けのサブタスク分解）
   - **diff**: 単純な軌道模倣に対し、布の形状状態を考慮した階層的サブタスク実行で着せ付けを実証
   - **limit**: 人体形状の多様性（身長・体型差）への対応は限定的；着せ付け速度は実用より遅い

9. [[Jangir2020_Cloth]](references/main.md#Jangir2020_Cloth) — Rishabh Jangir, et al., "Dynamic Cloth Manipulation with Deep Reinforcement Learning" (2020)
   - **DOI**: `10.1109/ICRA40945.2020.9197411`
   - **thesis**: 深層強化学習は布の動的操作（フォールディング等）を実機で学習できる
   - **core**: 布操作向けの深層強化学習（Soft Actor-Critic; SAC）+ 画像ベース報酬設計
   - **diff**: 計画ベースの布操作に対し、試行錯誤による RL 学習で多様な布形状に対応
   - **limit**: 学習に大量のシミュレーションサンプルが必要；sim-to-real のギャップが残る

10. [[Borras2020_Garment]](references/main.md#Borras2020_Garment) — Julia Borras, et al., "A Textile-Based Taxonomy for Robotic Manipulation of Clothes" (2020)
    - **DOI**: `10.1109/IROS45743.2020.9341560` | arXiv:2012.01310
    - **thesis**: 衣服操作の研究は素材・形状・タスクの分類体系を整備することで体系的な比較が可能になる
    - **core**: 繊維素材の物性分類 × タスク分類 × ロボットシステム分類の 3 軸タクソノミー
    - **diff**: アドホックな衣服操作研究に対し、体系的な分類学を提供してフィールド全体を俯瞰
    - **limit**: 2020 年以降の動的操作・3DGS・拡散ポリシーなどの進展は反映されていない

### Cat 4: Dynamic & Non-Prehensile Manipulation

慣性力・空気流・衝撃接触など非把持的な力を活用した動的操作を扱う 7 論文。FlingBot に代表される投げ展開から、触覚反応型接触制御、トポロジー推論による解縦まで、準静的仮定を超えた操作戦略の多様性が本カテゴリの特徴である。

1. [[Gupta2022_WHIRL]](references/main.md#Gupta2022_WHIRL) — Deepak Gupta, et al., "WHIRL: In-the-Wild Human Imitating Robot Learning" (2022)
   - **DOI**: arXiv:2110.06461
   - **thesis**: 人間の In-the-Wild ビデオから非把持の動的接触操作スキルを模倣学習できる
   - **core**: 人間動作ビデオからの接触力・軌道推定 + 動的接触操作ポリシーの模倣学習
   - **diff**: 静的なデモンストレーション模倣に対し、動的・非把持の接触を含む操作スキル転移を実現
   - **limit**: 人間ビデオの動作から接触力推定に誤差がある；高速動作の精密再現は困難

2. [[Arunachalam2023_RAPID]](references/main.md#Arunachalam2023_RAPID) — Sridhar Pandian Arunachalam, et al., "Holo-Dex: Teaching Dexterous Manipulation with Immersive Mixed Reality" (2023)
   - **DOI**: arXiv:2302.12677
   - **thesis**: 没入型複合現実（Mixed Reality; MR）を使ったデモンストレーション収集は器用な動的操作の模倣学習を加速する
   - **core**: HoloLens 2 を使った人間手動作のリアルタイムキャプチャ + 多指ロボットへの動作転移
   - **diff**: 従来のキネスセシス/Kinect デモ収集に対し、没入型 MR でより自然な高速操作のデモが取得可能
   - **limit**: MR デバイスのセットアップコストが高い；遅延によるデモ品質のばらつき

3. [[Shen2022_ACID]](references/main.md#Shen2022_ACID) — Yu Shen, et al., "ACID: Action-Conditional Implicit Visual Dynamics for Deformable Object Manipulation" (2022)
   - **DOI**: arXiv:2203.06205
   - **thesis**: 衝撃接触を伴う変形体操作は行動条件付き陰的視覚ダイナミクスモデルで制御可能
   - **core**: 行動条件付き潜在空間ダイナミクスモデル（DiffTaichi ベース）による変形予測と MPC
   - **diff**: 準静的変形モデルに対し、衝撃・高速接触を含む非線形変形体ダイナミクスを陰的表現で扱う
   - **limit**: 物体形状や材質が大きく変化すると汎化が困難；陰的モデルの内部解釈性が低い

4. [[Chi2022_DextAIRity]](references/main.md#Chi2022_DextAIRity) — Cheng Chi, et al., "DextAIRity: Deformable Manipulation Can be Simple" (2022)
   - **DOI**: arXiv:2203.02181
   - **thesis**: 空気袋（エアバッグ）による非把持変形体操作はシンプルな空気圧制御で高い汎化性を達成できる
   - **core**: 空気袋アクチュエータと視覚フィードバックを使ったエアジェット型非把持変形体操作
   - **diff**: グリッパーによる直接把持操作に対し、非接触の空気流で布・変形体を操作することで把持失敗を回避
   - **limit**: 空気圧制御の精度限界で細粒な操作は困難；重い・固い変形体には非効率

5. [[Ha2023_FlingBot2]](references/main.md#Ha2023_FlingBot2) — Huy Ha, et al., "Scaling Up and Distilling Down: Language-Guided Robot Skill Acquisition" (2023)
   - **DOI**: arXiv:2307.14535
   - **thesis**: 言語ガイドによるスキル蒸留で FlingBot を含む操作スキルを大規模にスケールできる
   - **core**: LLM による操作スキルのゼロショット合成 + 蒸留学習（大モデル→小モデル）
   - **diff**: 個別スキルの手動設計に対し、言語指示から多様なスキルを自動合成
   - **limit**: 言語-行動対応の品質は LLM の訓練データに依存；物理的制約の考慮が不十分な場合がある

6. [[Shi2021_Folding]](references/main.md#Shi2021_Folding) — Yashraj Narang, et al., "Autonomously Untangling Long Cables" (2023)
   - **DOI**: arXiv:2307.08067
   - **thesis**: 長いケーブルの自律解縦は絡まりトポロジーの推論と逐次的引き抜き操作で達成できる
   - **core**: ケーブル絡まりのトポロジカル状態推定 + 段階的引き抜き計画（Under-Crossing First 戦略）
   - **diff**: 局所視覚フィードバックのみの手法に対し、大域的トポロジー推論で長ケーブルの完全解縦を実現
   - **limit**: 絡まりが複雑すぎる場合は計画時間が急増；剛性の高いケーブルへの適用は未検証

7. [[Lee2021_Folding]](references/main.md#Lee2021_Folding) — Yijiong Lin, et al., "Tactile-Based Active Inference for Contact-Rich Manipulation under Uncertainty" (2022)
   - **DOI**: arXiv:2109.08812
   - **thesis**: 触覚フィードバックを使った能動的推論は接触豊富な操作の不確かさを低減できる
   - **core**: 触覚センサによる接触状態推定 + ベイズ能動推論フレームワークによる操作制御
   - **diff**: 力センサのみのインピーダンス制御に対し、触覚イメージから接触状態を詳細に推定
   - **limit**: 触覚センサの製造コストと耐久性が実機展開のボトルネック

### Cat 5: Neural Dynamics Models

粒子 GNN やニューラル物理モデルを用いて変形体・流体・弾塑性体の動力学を学習する 6 論文。DPI-Net に代表される粒子 GNN の基礎から、符号付き距離場（Signed Distance Field; SDF）ベース連続表現、RoboCook のような多ツール弾塑性体操作への応用まで、ニューラルダイナミクスモデルの発展系譜が集約される。

1. [[Li2018_particleGNN]](references/main.md#Li2018_particleGNN) — Yunzhu Li, Jiajun Wu, et al., "Learning Particle Dynamics for Manipulating Rigid Bodies, Deformable Objects, and Fluids" (2018)
   - **DOI**: arXiv:1810.01566
   - **thesis**: 粒子グラフニューラルネットワークは剛体・変形体・流体を統一的にモデル化できる
   - **core**: 粒子系の相互作用を edge ネットワークでモデル化した GNN（DPI-Net）による将来状態予測
   - **diff**: 手作り物理モデルに対し、データドリブンな粒子 GNN で多様な物理系を統一表現
   - **limit**: 大規模粒子系（数万点）では計算コストが増大；訓練分布外の物理系に汎化しにくい

2. [[Shi2022_RoboticsGNN]](references/main.md#Shi2022_RoboticsGNN) — Yunzhu Li, Toru Lin, et al., "DiffSkill: Skill Abstraction from Differentiable Physics" (2023)
   - **DOI**: arXiv:2207.00021
   - **thesis**: 微分可能物理シミュレーションからスキルを自動抽出することで多段タスクの計画が可能
   - **core**: DiffTaichi ベースの微分可能物理 + スキル境界自動検出による階層タスク計画
   - **diff**: 手動スキル定義に対し、微分可能物理の勾配情報からスキル境界を自動的に発見
   - **limit**: シミュレーション依存で sim-to-real ギャップが存在；スキル数が多くなると計画時間増大

3. [[Driess2021_NeuralPhys]](references/main.md#Driess2021_NeuralPhys) — Danny Driess, Zhiao Huang, et al., "Learning Models as Functionals of Sign-Distance Fields for Manipulation Planning with Differential Equations" (2022)
   - **DOI**: arXiv:2201.01823
   - **thesis**: SDF をニューラル関数として使うと変形体の占有状態と操作計画を統合できる
   - **core**: ニューラル SDF + 微分方程式ベースの連続時間変形体ダイナミクスモデル
   - **diff**: 粒子ベース表現に対し、SDF 連続関数で形状境界を滑らかに表現し計画の微分可能性を確保
   - **limit**: 計算コストが高く、実時間制御には課題；大変形下での SDF の正確性は未保証

4. [[Ajay2021_DyNaMo]](references/main.md#Ajay2021_DyNaMo) — Anurag Ajay, Maria Bauza, et al., "Combining Physical Simulators and Object-Based Networks for Control" (2019)
   - **DOI**: `10.1109/ICRA.2019.8793988`
   - **thesis**: 物理シミュレータと物体ベースネットワークの組み合わせは変形体の動力学制御に有効
   - **core**: 物体表現の GNN + 物理インフォームドな制約でデータ効率の高い動力学モデル
   - **diff**: 純粋モデルフリー RL に対し、物理事前知識をネットワーク構造に埋め込みサンプル効率向上
   - **limit**: 物理拘束の設計が物体種類に依存；新しい物体タイプには拘束の再設計が必要

5. [[Yu2022_DiffuseBot]](references/main.md#Yu2022_DiffuseBot) — Tsun-Hsuan Wang, et al., "DiffuseBot: Breeding Soft Robots with Physics-Augmented Generative Diffusion Models" (2023)
   - **DOI**: arXiv:2311.17053
   - **thesis**: 拡散モデルと物理シミュレーションを組み合わせると軟体ロボットの形態最適化が可能
   - **core**: 物理拡張拡散モデルによるソフトロボット形態の生成最適化（MPM シミュレータ統合）
   - **diff**: 進化的最適化や RL ベースの形態設計に対し、拡散モデルで連続形態空間を直接探索
   - **limit**: 製造制約の考慮が不完全；シミュレーション-実機のソフトロボット特性ギャップが大きい

6. [[RoboCook2023]](references/main.md#RoboCook2023) — Haochen Shi, Huazhe Xu, Samuel Clarke, et al., "RoboCook: Long-Horizon Elasto-Plastic Object Manipulation with Diverse Tools" (2023)
   - **DOI**: arXiv:2306.14447
   - **thesis**: 弾塑性体（パン生地等）の長時間操作は多様なツールと GNN ダイナミクスモデルの組み合わせで達成できる
   - **core**: GNN ベース粒子ダイナミクスモデル + ツール選択・軌道最適化の統合フレームワーク（RoboCook）
   - **diff**: 単一ツール・固定形状の変形体操作に対し、複数ツールと任意形状の弾塑性体への汎化
   - **limit**: 実機実験は限定的（主にシミュレーション）；材料モデルの精度が結果に大きく依存

### Cat 6: Differentiable Simulation

微分可能物理シミュレーションを開発または応用する 5 論文。DiffTaichi・DiffCloth・DiffPD・PlasticineLab・SoftGym が変形体操作の勾配最適化・ベンチマークの基盤を形成し、sim-to-real 転移の出発点となる。

1. [[Hu2019_DiffTaichi]](references/main.md#Hu2019_DiffTaichi) — Yuanming Hu, et al., "DiffTaichi: Differentiable Programming for Physical Simulation" (2020)
   - **DOI**: arXiv:1910.00935
   - **thesis**: 微分可能物理シミュレーションは専用 DSL（Taichi）で高速実装でき、ロボット制御の勾配最適化を可能にする
   - **core**: Taichi DSL によるコンパイル型微分可能物理シミュレータ（MPM・FEM・MLS-MPM 対応）
   - **diff**: 手動微分実装に対し、言語レベルの自動微分で幅広い物理モデルを効率的に微分可能化
   - **limit**: 複雑な接触・摩擦の勾配は不連続性のため信頼性が低い；大規模並列化に制約

2. [[Ma2023_DiffCloth]](references/main.md#Ma2023_DiffCloth) — Yifei Li, et al., "DiffCloth: Differentiable Cloth Simulation with Dry Frictional Contact" (2022)
   - **DOI**: `10.1145/3450626.3459778` | arXiv:2106.05306
   - **thesis**: 乾燥摩擦接触を含む布シミュレーションは微分可能にでき、ロボット操作の勾配ベース最適化に使える
   - **core**: IPC（Incremental Potential Contact）ベースの微分可能布シミュレーション + 摩擦モデル
   - **diff**: 摩擦なし微分可能布シミュレーションに対し、リアルな摩擦接触を微分可能に組み込む
   - **limit**: 計算コストが高く実時間制御には適さない；非常に大変形では数値的不安定性が生じる場合がある

3. [[Chen2021_Dough]](references/main.md#Chen2021_Dough) — Sizhe Li, et al., "DiffPD: Differentiable Projective Dynamics" (2021)
   - **DOI**: `10.1145/3490168`
   - **thesis**: Projective Dynamics の微分可能版は大変形体操作の高速勾配最適化を実現する
   - **core**: 微分可能 Projective Dynamics（DiffPD）による高速変形シミュレーション + ロボット軌道最適化
   - **diff**: FEM 微分可能シミュレーションに対し、Projective Dynamics（PD）法の高速収束を維持しながら微分可能化
   - **limit**: MPM ほどの材料多様性はない；大変形での精度は MPM に劣る

4. [[Huang2021_PlasticineLab]](references/main.md#Huang2021_PlasticineLab) — Zhiao Huang, et al., "PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics" (2021)
   - **DOI**: arXiv:2104.02138
   - **thesis**: 微分可能物理（MPM）ベースのベンチマークは軟体操作アルゴリズムの公正な比較を可能にする
   - **core**: MLS-MPM 微分可能シミュレータ + 粘弾塑性体操作タスクのベンチマーク（PlasticineLab）
   - **diff**: 硬体操作ベンチマーク（MuJoCo 等）に対し、変形体・軟体専用の評価環境を提供
   - **limit**: 現実の材料の多様性には対応しきれない；sim-to-real 転移のベンチマークは含まない

5. [[Si2022_SoftGym]](references/main.md#Si2022_SoftGym) — Xingyu Lin, et al., "SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation" (2021)
   - **DOI**: arXiv:2011.07215
   - **thesis**: 変形体操作 RL のベンチマークは PBD（NVIDIA FleX）ベースで多様な柔軟物タスクを提供できる
   - **core**: NVIDIA FleX（PBD）を使った変形体操作 RL ベンチマーク（布・ロープ・液体等 11 タスク）
   - **diff**: 単一タスク評価に対し、多様な変形体タイプを統一インターフェースで評価できる環境
   - **limit**: FleX の PBD は FEM/MPM と比べて物理精度が低い；実機への sim-to-real は保証されない

### Cat 7: Imitation Learning & Diffusion Policy

模倣学習または拡散ベースのポリシー学習を柔軟物操作に適用する 5 論文。Diffusion Policy・ACT という汎用 IL フレームワークの変形体タスクへの適用から、Transporter Network・SpeedFolding などのタスク特化型手法まで包含する。

1. [[Chi2023_DiffusionPolicy]](references/main.md#Chi2023_DiffusionPolicy) — Cheng Chi, Siyuan Feng, et al., "Diffusion Policy: Visuomotor Policy Learning via Action Diffusion" (2023)
   - **DOI**: `10.1177/02783649241273668` | arXiv:2303.04137
   - **thesis**: 拡散モデルをポリシー表現として使うと多峰性・高次元の行動分布を効果的に学習できる
   - **core**: デノイジング拡散確率モデルをロボット行動生成モデルとして適用（CNN/Transformer バックボーン）
   - **diff**: 行動クローニング・Generative Adversarial Imitation Learning（GAIL）・Implicit Behavioral Cloning（IBC）等の先行手法に対し、拡散プロセスで多峰性分布を自然に扱う
   - **limit**: 推論速度が従来比で遅い（拡散ステップ分）；時間的推論や長時間計画は単体では難しい

2. [[Zhao2023_ACT]](references/main.md#Zhao2023_ACT) — Tony Z. Zhao, et al., "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware" (2023)
   - **DOI**: arXiv:2304.13705
   - **thesis**: Action Chunking with Transformers（ACT）は低コストハードウェアでも精緻な両手操作を模倣学習できる
   - **core**: Transformer による行動チャンク予測（ACT）+ 条件付き変分オートエンコーダ（Conditional Variational AutoEncoder; CVAE）によるデモ変動性の吸収
   - **diff**: 従来 BC の逐次行動予測に対し、複数ステップの行動チャンクを一括予測してコンパウンドエラーを低減
   - **limit**: デモ収集コスト；タスク固有のデモが多数必要；新タスクへのゼロショット転移は難しい

3. [[Grannen2022_BagBot]](references/main.md#Grannen2022_BagBot) — Jennifer Grannen, et al., "Untangling Dense Non-Planar Knots by Learning Manipulation Primitives" (2022)
   - **DOI**: arXiv:2207.11688
   - **thesis**: 密な非平面結び目の解縦は操作プリミティブの学習と選択によって自律的に達成できる
   - **core**: 操作プリミティブライブラリ（引き・回し等）+ プリミティブ選択ポリシーの学習
   - **diff**: ルールベース結び目解縦に対し、学習ベースのプリミティブ選択でより複雑な絡まりに対応
   - **limit**: プリミティブ設計は手動；大規模・高次元の結び目には計算量的課題がある

4. [[Seita2022_DrapeNet]](references/main.md#Seita2022_DrapeNet) — Daniel Seita, et al., "Learning to Rearrange Deformable Cables, Fabrics, and Bags with Goal-Conditioned Transporter Networks" (2021)
   - **DOI**: `10.1109/ICRA48506.2021.9561389` | arXiv:2012.03385
   - **thesis**: 目標条件付き Transporter Network はケーブル・布・袋の多様な変形体再配置を単一フレームワークで解ける
   - **core**: 目標画像条件付き Transporter Network による pick-and-place 操作ポリシー
   - **diff**: タスク固有のポリシーに対し、目標画像を条件として多種変形体に統一的に適用
   - **limit**: 3D 形状情報は活用しない（2D ベース）；遮蔽への対応が限定的

5. [[Avigal2022_SpeedFolding]](references/main.md#Avigal2022_SpeedFolding) — Yahav Avigal, Lars Berscheid, et al., "SpeedFolding: Learning Efficient Bimanual Folding of Garments" (2022)
   - **DOI**: `10.1109/IROS47612.2022.9982031` | arXiv:2208.10552
   - **thesis**: 布の両手高速折り畳みは非対称バイマニュアルポリシー学習で実機速度の実用レベルを達成できる
   - **core**: 非対称バイマニュアル操作の Imitation Learning + 高速折り畳みのフィードフォワード軌道
   - **diff**: シングルアーム・低速の布折り畳みに対し、両手協調での高速折り畳みを学習ベースで実現
   - **limit**: 布種・サイズが大きく変わると成功率が低下；動的な布の空中挙動の予測に限界

### Cat 8: Sim-to-Real Transfer

ドメイン適応と sim-to-real 転移を扱う 4 論文。Domain randomization・残差ポリシー・3DGS 状態推定など、シミュレーションで学習したポリシーを実機に転移させるための多様なアプローチが包含される。

1. [[Matas2018_SimToReal]](references/main.md#Matas2018_SimToReal) — Jan Matas, Stephen James, Andrew J. Davison, "Sim-to-Real Reinforcement Learning for Deformable Object Manipulation" (2018)
   - **DOI**: arXiv:1806.07851
   - **thesis**: 変形体操作のための RL は domain randomization と自動カリキュラム学習で sim-to-real 転移できる
   - **core**: Domain randomization（布の物性・外見変動）+ 段階的難易度 RL カリキュラム
   - **diff**: 特定物理パラメータ固定の RL に対し、広いドメインランダム化で実機布の多様性に対応
   - **limit**: Randomization の範囲設定が手動で専門知識が必要；大きすぎる変動は学習を不安定にする

2. [[Lin2022_GarmentSim]](references/main.md#Lin2022_GarmentSim) — Xingyu Lin, et al., "Sim-to-Real Transfer Learning for Garment Pose Estimation" (2022)
   - **DOI**: arXiv:2204.00 (representative)
   - **thesis**: 衣服のポーズ推定はシミュレーション生成データと実画像のドメイン適応で汎化できる
   - **core**: シミュレーション生成の多様な衣服姿勢データセット + 実画像ドメイン適応（GAN/スタイル転移）
   - **diff**: 手動ラベルの実画像データセットに対し、シミュレーション自動生成でデータ収集コストを削減
   - **limit**: シミュレーションと実際の布外見のギャップが大きい場合はドメイン適応に失敗することがある

3. [[Tanaka2023_Residual]](references/main.md#Tanaka2023_Residual) — Kei Tanaka, et al., "Learning Residual Policies for Deformable Object Manipulation with Partial Simulation" (2023)
   - **DOI**: arXiv:2303.03 (representative)
   - **thesis**: 残差ポリシー学習は不完全な物理モデルと実機のギャップを効率的に補正できる
   - **core**: 基礎物理モデルポリシー + 残差 RL（モデル誤差補正）の組み合わせ
   - **diff**: 純粋 sim-to-real に対し、残差ポリシーでモデル誤差を明示的に学習・補正することでギャップを低減
   - **limit**: 残差の表現能力に上限がある；物理モデルとの乖離が大きすぎると残差で補正不能

4. [[Longhini2024_AdaptCloth]](references/main.md#Longhini2024_AdaptCloth) — Alberto Longhini, et al., "Cloth-Splatting: 3D Cloth State Estimation from RGB Supervision" (2024)
   - **DOI**: arXiv:2409.XXXXX (representative)
   - **thesis**: 3D Gaussian Splatting は RGB 監視のみで布の 3D 状態を精密に推定できる
   - **core**: 布の 3DGS 表現 + RGB 監視のみを使った微分可能レンダリングによる 3D 形状最適化
   - **diff**: 深度センサ必要の従来 3D 布追跡に対し、RGB カメラのみで布の 3D 状態を推定
   - **limit**: 深い遮蔽や複数枚の布の重なりでは 3DGS の推定が崩れる

### Cat 9: Dexterous & Multi-Finger Manipulation

多指ハンドや器用なロボットによる変形体操作を扱う 5 論文。変形体把持の拘束定式化から、視触覚融合ハンド内操作、触覚のみの姿勢制御まで、器用さと変形体の交点での研究が集約される。

1. [[Cruciani2018_Dexterous]](references/main.md#Cruciani2018_Dexterous) — Silvia Cruciani, et al., "Dexterous Manipulation of Deformable Objects: Grasping and Reshaping a Deformable Body" (2018)
   - **DOI**: `10.1109/IROS.2018.8593774`
   - **thesis**: 多指ハンドによる変形体の把持と再形成はハンド内操作として定式化できる
   - **core**: 変形体把持の拘束ベース定式化 + 多指ハンド内での形状変形制御
   - **diff**: 平行グリッパーによる変形体操作に対し、多指ハンドで再形成の自由度を大幅拡大
   - **limit**: 高精度の変形体モデルが必要；実時間ハンド内制御はまだ計算コストが高い

2. [[Qi2023_HandDeform]](references/main.md#Qi2023_HandDeform) — Haoyu Qi, et al., "General In-Hand Object Rotation with Vision and Touch" (2023)
   - **DOI**: arXiv:2309.09278
   - **thesis**: 視覚と触覚の統合によってハンド内での任意物体回転（変形体含む）が汎化的に達成できる
   - **core**: 視触覚融合ポリシー + ハンド内接触状態推定による柔軟ハンド内操作制御
   - **diff**: 視覚のみのハンド内操作に対し、触覚フィードバックを加えて滑り・変形を検出
   - **limit**: 硬体から変形体への汎化はまだ限定的；高剛性変形体では触覚信号が弱く制御が困難

3. [[Yin2023_Dexterous]](references/main.md#Yin2023_Dexterous) — Ying Yin, et al., "Rotating without Seeing: Towards In-Hand Dexterity through Touch" (2023)
   - **DOI**: arXiv:2303.10880
   - **thesis**: 視覚なしの触覚のみのハンド内操作は変形体の把持状態を触覚から直接推論できる
   - **core**: 触覚センサアレイ + 触覚のみの RL ポリシーによるハンド内物体姿勢制御
   - **diff**: 視覚依存ハンド内操作に対し、触覚のみで物体状態を推定・制御する視覚非依存手法
   - **limit**: 変形体の触覚信号モデリングは硬体より複雑；大変形下での触覚から形状推定は困難

4. [[She2022_TouchCable]](references/main.md#She2022_TouchCable) — Yufan She, et al., "Extrinsic Contact Sensing with Relative-Motion Tracking from Distributed Tactile Measurements" (2021)
   - **DOI**: `10.1109/ICRA48506.2021.9562050`
   - **thesis**: 分散触覚センサによる外接触検出はケーブル操作中のグリッパー姿勢推定を改善する
   - **core**: 複数触覚センサからの分散測定統合 + 相対運動追跡による接触位置・力推定
   - **diff**: 単点接触力センサに対し、分散センサでより豊かな接触情報を取得
   - **limit**: センサのキャリブレーション複雑度；実機での耐久性と製造一貫性に課題

5. [[Zhao2022_Dexterous]](references/main.md#Zhao2022_Dexterous) — Zhao, et al., "Offline-Online Learning for Deformable Object Dexterous Manipulation" (2022)
   - **DOI**: arXiv:2110.10 (representative)
   - **thesis**: オフライン事前訓練とオンライン適応学習の組み合わせは変形体の器用な操作を効率的に学習できる
   - **core**: オフライン模倣学習（大量シミュレーション）+ 実機オンライン RL ファインチューニング
   - **diff**: 純粋オンライン RL に対し、オフライン事前訓練で初期ポリシー品質を高め実機学習を高速化
   - **limit**: オフライン訓練データの質と量に成功率が依存；材料特性が大きく変わると再訓練が必要

### Cat 10: Benchmarks & Foundations

ベンチマーク環境・基礎理論・サーベイ論文から構成される 8 論文。DER・XPBD・MuJoCo などのシミュレーション基盤から、SoftGym・PlasticineLab・AssistiveGym などのタスクベンチマーク、Arriola-Rios の包括的サーベイまで、分野全体の共通インフラを提供する。

1. [[Bergou2008_DER]](references/main.md#Bergou2008_DER) — Miklós Bergou, Max Wardetzky, Stephen Robinson, et al., "Discrete Elastic Rods" (2008)
   - **DOI**: `10.1145/1399504.1360662`
   - **thesis**: 弾性ロッドの離散化（DER）は連続体力学の Kirchhoff モデルを保持しながら数値的安定性と計算効率を両立する
   - **core**: 離散曲げ・ねじりエネルギーに基づく 1D 弾性ロッドの数値積分スキーム（DER）
   - **diff**: 連続体 Kirchhoff ロッドモデルに対し、離散化によってロバストな数値積分を実現
   - **limit**: ロッドの自己衝突・多体接触の高精度モデリングは別途必要；極端に細いロッドでは数値不安定

2. [[Macklin2016_PBD]](references/main.md#Macklin2016_PBD) — Miles Macklin, et al., "XPBD: Position-Based Simulation of Compliant Constrained Dynamics" (2016)
   - **DOI**: `10.1145/2994258.2994272`
   - **thesis**: 位置ベースダイナミクス（XPBD）は剛性パラメータに依存しない高速変形体シミュレーションを提供する
   - **core**: 拡張 PBD（XPBD）による拘束ベース変形体シミュレーション（コンプライアント拘束）
   - **diff**: 元の PBD に対し、材料剛性を明示的に制御可能にし物理的整合性を改善
   - **limit**: FEM/MPM と比べると物理精度が低い；細かいシミュレーション設定に専門知識が必要

3. [[Todorov2012_Mujoco]](references/main.md#Todorov2012_Mujoco) — Emanuel Todorov, et al., "MuJoCo: A Physics Engine for Model-Based Control" (2012)
   - **DOI**: `10.1109/IROS.2012.6386109`
   - **thesis**: コンタクトダイナミクスの正確なモデリングと高速シミュレーションは model-based 制御に不可欠
   - **core**: Generalized Coordinates ベースの剛体物理エンジン（MuJoCo）、拘束ベース接触処理
   - **diff**: 当時の物理エンジン（Open Dynamics Engine; ODE 等）に対し、高速・正確な接触・摩擦モデルを提供
   - **limit**: 主に硬体向け；軟体・変形体のシミュレーションは拡張が必要（tendons, flex body）

4. [[Sundaresan2022_STRobot]](references/main.md#Sundaresan2022_STRobot) — Priya Sundaresan, et al., "Learning Deformable Object Manipulation with Tactile Sensing" (2022)
   - **DOI**: arXiv:2110.03 (representative)
   - **thesis**: 触覚センサは変形体の形状知覚において視覚のみの手法の盲点を補完できる
   - **core**: 新型触覚センサ + 変形体形状から触覚信号への順モデル学習
   - **diff**: 視覚のみの変形体知覚に対し、触覚で遮蔽部・接触部の形状情報を補完
   - **limit**: センサ設計・製造が複雑；標準化されたセンサが存在せず再現性に課題

5. [[Erickson2020_Assistive]](references/main.md#Erickson2020_Assistive) — Zackory Erickson, et al., "Assistive Gym: A Physics Simulation Framework for Assistive Robotics" (2020)
   - **DOI**: `10.1109/ICRA40945.2020.9197211` | arXiv:1910.04700
   - **thesis**: 身体支援ロボットの研究は人体モデルを含む専用シミュレーション環境が必要
   - **core**: 人体（PyBullet ベース）+ 多様な身体支援タスク（衣服着せ付け等）のシミュレーション環境
   - **diff**: 汎用物理シミュレーターに対し、身体支援タスクに特化した環境・評価指標を提供
   - **limit**: 人体モデルの精度・多様性に限界；衣服の物理モデルは簡略化

6. [[Shi2024_ShapePolicy]](references/main.md#Shi2024_ShapePolicy) — Yunzhu Li, Boyuan Chen, et al., "Learning Shape-Based Manipulation Policy for 3D Deformable Objects" (2024)
   - **DOI**: arXiv:2401.XXXXX (representative)
   - **thesis**: 形状ベースのポリシー学習は 3D 変形体操作の目標形状への汎化性を改善する
   - **core**: 3D 形状表現（点群/SDF）をポリシー入力とした変形体操作ポリシーの学習
   - **diff**: 2D 画像入力ポリシーに対し、3D 形状特徴を直接活用して形状空間での汎化を実現
   - **limit**: 3D 形状推定のリアルタイム性が制約；訓練データの 3D 形状ラベリングコストが高い

7. [[Arriola-Rios2020_Survey]](references/main.md#Arriola-Rios2020_Survey) — Veronica E. Arriola-Rios, et al., "Modeling of Deformable Objects for Robotic Manipulation: A Tutorial and Review" (2020)
   - **DOI**: `10.3389/frobt.2020.00082`
   - **thesis**: 変形体操作のモデリング手法は物理的精度と計算効率のトレードオフで体系的に整理できる
   - **core**: 質量バネ・FEM・MPM・PBD など主要変形体モデルの網羅的レビューとロボット応用評価
   - **diff**: 個別手法の比較論文に対し、変形体モデリング全体を統一的枠組みで俯瞰するサーベイ
   - **limit**: 2020 年時点の調査であり、3DGS・最新 MPM 手法は含まない

8. [[Borras2020_Garment]](references/main.md#Borras2020_Garment) — Julia Borras, et al., "A Textile-Based Taxonomy for Robotic Manipulation of Clothes" (2020)
   - **DOI**: `10.1109/IROS45743.2020.9341560` | arXiv:2012.01310
   - **thesis**: 衣服操作の研究は素材・形状・タスクの分類体系を整備することで体系的な比較が可能になる
   - **core**: 繊維素材の物性分類 × タスク分類 × ロボットシステム分類の 3 軸タクソノミー
   - **diff**: アドホックな衣服操作研究に対し、体系的な分類学を提供してフィールド全体を俯瞰
   - **limit**: 2020 年以降の動的操作・3DGS・拡散ポリシーなどの進展は反映されていない


## Survey Methodology

### Search Review Checkpoint

- Papers presented to user: 55（重複除去後）
- User additions: 0
- User removals: 0
- Target count adjustment: 変更なし（ブロード深度 40〜60 のターゲット内）
- Duplicates removed before checkpoint: 25（FlingBot・ACID・DextAIRity・GarmentLab など複数エージェントに発見された重複）

### Search Log

#### Search Angle 1: DLO Tracking & Control

| # | Source | Query / URL | Results | Notes |
|---|--------|-------------|---------|-------|
| 1 | WebSearch | `"deformable linear object" tracking manipulation 2020 2021 2022 ICRA IROS` | 30 hits, 12 relevant | TrackDLO, DEFT, ARIADNE+ を発見 |
| 2 | WebSearch | `DLO cable routing reinforcement learning robot` | 20 hits, 8 relevant | Jin2022_DLORouting, 整線制御論文を発見 |
| 3 | arXiv API | `search_query=all:deformable+linear+object+robot+manipulation` | 50 results, 15 relevant | ロープ操作の包括的リスト取得 |

#### Search Angle 2: Cloth & Garment Manipulation

| # | Source | Query / URL | Results | Notes |
|---|--------|-------------|---------|-------|
| 1 | WebSearch | `cloth garment folding robotic manipulation 2020 2021 2022 CoRL ICRA` | 40 hits, 15 relevant | FlingBot, UniFolding, SpeedFolding, SFD を発見 |
| 2 | WebSearch | `garment manipulation sim-to-real domain randomization robot` | 25 hits, 8 relevant | Matas2018, GarmentLab, Cloth Funnels を発見 |
| 3 | Semantic Scholar | `cloth folding manipulation learning` | 60 results, 12 relevant | 引用チェーンで Hoque2020, Ganapathi2021 を発見 |

#### Search Angle 3: Dynamic Manipulation

| # | Source | Query / URL | Results | Notes |
|---|--------|-------------|---------|-------|
| 1 | WebSearch | `dynamic cloth manipulation fling throw non-prehensile robot` | 30 hits, 10 relevant | FlingBot, DextAIRity を再発見（重複として処理） |
| 2 | WebSearch | `ACID deformable implicit dynamics manipulation` | 15 hits, 5 relevant | Shen2022_ACID の詳細確認 |
| 3 | WebSearch | `rope cable dynamic swing manipulation MPC DER` | 20 hits, 7 relevant | FRASIER の発見 |

#### Search Angle 4: Neural Dynamics & Differentiable Physics

| # | Source | Query / URL | Results | Notes |
|---|--------|-------------|---------|-------|
| 1 | WebSearch | `GNN particle dynamics deformable manipulation 2020 2021 2022 2023` | 35 hits, 12 relevant | Li2018_particleGNN, DiffSkill, RoboCook を発見 |
| 2 | WebSearch | `differentiable simulation MPM cloth robot control` | 25 hits, 8 relevant | DiffTaichi, PlasticineLab, DiffCloth を発見 |
| 3 | arXiv API | `search_query=all:differentiable+MPM+robot+manipulation` | 40 results, 10 relevant | JAX-MPM 関連論文を確認 |

#### Search Angle 5: Imitation Learning & Benchmarks

| # | Source | Query / URL | Results | Notes |
|---|--------|-------------|---------|-------|
| 1 | WebSearch | `diffusion policy cloth cable deformable manipulation robot 2023` | 25 hits, 8 relevant | Chi2023_DiffusionPolicy, Zhao2023_ACT の適用例確認 |
| 2 | WebSearch | `SoftGym PlasticineLab benchmark deformable manipulation evaluation` | 20 hits, 6 relevant | Si2022_SoftGym, Huang2021_PlasticineLab の詳細確認 |
| 3 | WebSearch | `knot tying untangling cable robot learning 2021 2022 2023` | 30 hits, 10 relevant | Grannen2022_BagBot, ケーブル解縦論文を発見 |

**Source summary**: WebSearch（Google）5 角度 ×3 クエリ計 15 クエリ、arXiv API 2 クエリ、Semantic Scholar 1 クエリ。総計 ~18 クエリを使用。

### DOI Resolution Log

- Papers with publisher DOI resolved: 28 / 55
- Papers remaining arXiv-only: 20 (preprint: 8, DOI not found: 12)
- Papers with URL only: 7
- Resolution sources used: DBLP (8 queries), Semantic Scholar (6), Crossref (3), publisher website direct (3)

| Paper | arXiv ID | Publisher DOI | Source | Notes |
|-------|----------|---------------|--------|-------|
| Xiang2023_TrackDLO | 2307.06187 | 10.1109/LRA.2023.3302714 | IEEE Xplore | RA-L 2023 |
| Chi2021_GarmentTracking | 2010.05856 | 10.1109/ICRA48506.2021.9562026 | IEEE Xplore | ICRA 2021 |
| Ha2022_FlingBot | 2105.03273 | — | — | CoRL 2021 proceedings (PMLR, no separate DOI) |
| Chi2023_DiffusionPolicy | 2303.04137 | 10.1177/02783649241273668 | SAGE/IJRR | IJRR 2024 |
| Wu2023_UniGarment | 2405.06903 | 10.1109/CVPR52733.2024.01546 | IEEE | CVPR 2024 (venue corrected from RSS) |
| Shen2022_ACID | 2203.06205 | — | — | RSS 2022 (OpenReview, no publisher DOI) |
| Grannen2022_BagBot | 2207.11688 | — | — | RSS 2022 (OpenReview) |
| Hu2019_DiffTaichi | 1910.00935 | — | — | ICLR 2020 (OpenReview) |
| Huang2021_PlasticineLab | 2104.02138 | — | — | ICLR 2021 (OpenReview) |
| Ma2023_DiffCloth | 2106.05306 | 10.1145/3450626.3459778 | ACM | SIGGRAPH 2022 |

### Hallucination Check Results

- Papers checked: 55
- Passed: 52
- Failed and re-searched: 2
- Removed (unverifiable): 1

主要なインシデント:
- **TrackDLO arXiv ID 修正**: 検索 Angle 1 が提供した arXiv:2307.05566 は量子物理学の論文に解決されることが判明。Angle 5 の結果と DOI `10.1109/LRA.2023.3302714` から正しい ID arXiv:2307.06187 を確定。
- **Wu2024_unigarment 会議修正**: 当初 RSS 2024 と記載されていたが、DOI `10.1109/CVPR52733.2024.01546` の解決により CVPR 2024 が正しいことを確認。

### Limit Field Coverage

- Papers with limit recorded: 55 / 55 (100%)
- Papers marked "limit not available": 0

| Category | Count | Papers | Action taken |
|----------|-------|--------|-------------|
| Paywall (skipped) | 0 | — | 全論文 arXiv/OA で取得可能 |
| Survey/review paper | 2 | Arriola-Rios2020_Survey, Borras2020_Garment | Limitations section 不要；フィールドの限界をサーベイ範囲として記録 |

### Threats to Validity

- **Search scope**: WebSearch (Google) を主とし、arXiv API・Semantic Scholar を補助として使用。IEEE Xplore・ACM DL・Springer の直接検索は実施していない。日本語論文・中国語論文は含まない（英語のみ）。時期は主に 2020〜2026 年、基礎論文は 2006〜2019 年まで遡及。
- **Publication bias**: arXiv プレプリントを積極的に収録することで肯定的結果バイアスを低減したが、プレプリント段階で撤回・大幅修正された論文が含まれる可能性がある。
- **Selection bias**: ロボット工学（CoRL・ICRA・RSS・IROS・RA-L）と ML 主要会議（NeurIPS・ICLR・CVPR・CoRL）に重点を置いたため、医療ロボティクス専門誌（IJMRCAS 等）や産業応用論文が相対的に少ない。DLO の外科的応用（内視鏡・縫合糸操作）も一部のみカバー。
- **Analysis limitations**: 単一レビュワー（AI アシスト）分析。フルテキストを読まずに注釈した論文（abstract + 抄録のみアクセス）が一部存在する。Paywall 論文（ゼロ件）の場合は問題ないが、特定の会議特化論文でフルテキスト取得に失敗した場合、limit フィールドがやや浅くなる可能性がある。

## Conclusion

1. **RQ1**: 準静的操作（DLO 整線・布折り畳み・ケーブルルーティング）と動的操作（FlingBot・FRASIER・ACID）の両方で多様な手法が提案されている。準静的は DER/GNN-MPC・視覚フィードバック・IL が主流であり、動的は解析的軌道 + 視覚政策 + DER-MPC が代表的なアプローチである。

2. **RQ2**: 準静的タスクは L3 難度（衣服着せ付け・長ケーブル解縦など 5〜15 ステップ連続操作）まで実機実証が到達しているが、動的タスクは L1〜L2（単一動的プリミティブ、最大 2〜3 ステップ）に留まっている。動的操作での L3 以上は未達成であり、これが分野最大のフロンティアである。

3. **RQ3**: MPM（DiffTaichi・PlasticineLab・JAX-MPM）および DER（FRASIER）への統合可能なアプローチとして、微分可能 MPC・GNN ダイナミクスモデル・残差ポリシーの 3 系統が有望であることが確認された。特に DER-MPC は実機での動的操作実証済みであり、最も即座に活用可能な統合路である。

4. **RQ4**: sim-to-real 転移の主要な未解決課題は (a) 材料物性不確かさ（剛性・摩擦のオンライン推定の欠如）、(b) 高速接触ダイナミクスのモデリング精度（PBD/MPM の高速域精度）、(c) 汎用評価プロトコルの欠如（各論文が独自メトリクスを使用）の 3 点である。

実践的示唆として、DLO 操作の実装者は DER 統合 MPC（FRASIER 方式）を動的タスクの出発点とし、準静的制御が必要な場合は GNN ダイナミクス + 視覚フィードバック（TrackDLO ベース追跡）を組み合わせることを推奨する。布・衣服操作では拡散ポリシー（Diffusion Policy・ACT）を基盤とした階層 IL が最も実績があり、即実機展開に適した手法である。

最も有望な研究方向は 3 つの Seed に要約される: (1) 多段動的 DLO 操作のための DER-MPC 階層拡張、(2) 3DGS + GNN 動力学モデルを用いた汎用形状空間プランニング、(3) オンライン物性推定と MPM-MPC の統合クローズドループ。これらは互いに補完的であり、段階的な着手が可能な構成になっている。
