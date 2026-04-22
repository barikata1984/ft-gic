# Literature Survey: Physical Property Estimation of Deformable Objects for Robot Manipulation

**Date**: 2026-04-21  
**Surveyor**: Claude Sonnet 4.6 (literature-survey skill)  
**Topic**: 変形可能物体の形状・物性（質量・ヤング率・ポアソン比）の復元とロボットマニピュレータによる操作への応用  
**Depth**: focused (41 papers, 2018–2026)  
**Seed**: included

---

## Research Questions

- **RQ1**: 変形可能物体の物性（質量・ヤング率・ポアソン比）を復元するためにどのようなアルゴリズム・表現（3DGS、MPM、バネマス系など）が提案されているか？
- **RQ2**: 推定した物性はどのような実世界ロボットタスクに応用されているか？各タスクで達成された精度・再現性はどの程度か？
- **RQ3**: シミュレーションと実世界の間のギャップ（sim-to-real）はどのように扱われているか？物性推定の精度がロボット制御品質に与える影響は？
- **RQ4**: 未解決の課題（接触不連続・不均質材料・リアルタイム推定・実タスクへの統合）はどこにあるか？

---

## Survey Findings

### Thesis（フィールドの根本的な未解決問題）

変形可能物体の物理特性推定が本質的に困難である理由は、まず「観測可能性と推定可能性の乖離」という根本的な問題に起因する。変形挙動は質量・ヤング率・ポアソン比・摩擦係数・粘性などの複数パラメータの非線形結合として現れるが、実際にロボットが観測できるのはRGB-深度 (RGB-D) 映像や力センサの時系列信号に過ぎない。この逆問題は本質的に不良設定（ill-posed）であり、同一の観測から異なるパラメータセットが等価な挙動を生成しうる。Yang2024_DPSIはこれを「鞍点問題」として明示し、Li2023_PACNeRFは既知の物体形状を仮定せずに幾何形状と物理パラメータを同時に推定することがいかに困難かを示した。Patni2024_OnlineElasticityは標準的な平行グリッパを用いた場合、絶対値としてのヤング率回復には装置間で2倍以上の誤差が生じることを実証し、「相対的識別は可能でも絶対推定は困難」という現実を定量的に示している。

第二の根本問題は「シミュレーションモデルと現実の構成則の乖離」である。MPM・FEM・バネ質点系などの物理シミュレータは、均質・等方・連続体という仮定のもとで動作するが、実際の変形物体（外科組織・布・ロープ・食品）は不均質・異方性・粘弾塑性的な挙動を示す。ThinShellLab（Wang2024）は曲げ剛性と塑性を同時にモデル化しなければ薄板の操作が再現できないことを示し、Li2024_BayesianDiffPhysicsは空間的に不均質なパラメータ分布をベイズ推定で扱う必要性を論じた。Scheikl2023_RealtoSimは残差写像とオンライン剛性最適化の組み合わせなしには手術組織のsim-to-real転移が成立しないことを示しており、いかなる単一の物理モデルも実世界の複雑性を完全にカバーできないことを示唆する。

第三の問題は「計算コストとリアルタイム性の二律背反」である。微分可能シミュレーション（DiffTaichi: Hu2020、SoftMAC: Liu2024）は高精度な勾配情報を提供するが、接触不連続や大変形時の数値的不安定性により最適化ランドスケープが平坦化する。PIDG（Zheng2025）は単眼動画からの物理整合再構成に数時間から数日を要し、DiffTactile（Chen2024）の逆方向微分は順方向の2倍の計算コストを必要とする。AdaptiGraph（Lin2024）やSoMA（Huang2026）のようなニューラルダイナミクスアプローチはリアルタイム動作を実現するが、汎化性能と推定精度のトレードオフが依然として解消されていない。これらの問題が複合することで、「高精度・リアルタイム・汎用的なパラメータ推定」という三つの目標を同時に達成する方法は現時点では存在しない。

---

### Foundation（共有される技術的基盤）

**Building Block 1: 微分可能物理シミュレーション (Differentiable Physics Simulation)**

最も広く共有される技術的基盤は、シミュレーション全体を通じた勾配逆伝播を可能にする微分可能物理エンジンである。Hu2020_DiffTaichiはソースコード変換とテープによる二段階微分を提供し、後続研究の根幹を成す。これを継承してHuang2021_PlasticineLab はVon Mises降伏を含む弾塑性MPMを微分可能化し、Yang2024_DPSI・Chen2026_EMPM・Yang2025_DDBot はそれぞれ実ロボット実験での材料同定に適用した。布・薄板系ではWang2024_ThinShellLab・Zheng2024_DiffCPが独自の微分可能定式化を採用し、変形線形物体 (Deformable Linear Object; DLO) 系ではCheng2024_DEFORMがPyTorchによる微分可能離散弾性ロッド (Discrete Elastic Rods; DER) を実装した。損失関数としてChamfer距離・Earth Mover's Distance (EMD)・測光ロスが共通して用いられる。

**Building Block 2: 3Dガウシアンスプラッティング (3DGS) による形状・動態表現**

視覚的リアリティと物理演算の橋渡しとして、3DGSが急速に標準表現として台頭している。Xie2023_PhysGaussianはガウシアン核に変形勾配とストレステンソルを付加し、MPM時間発展と連動させる「見たものをシミュレートする (What You See is What You Simulate; WS2) 原理」を提案した。これを発展させたのがLiu2024_Physics3D（粘弾性）・Wang2025_OmniPhysGS（12構成則自動選択）・Li2025_PhysGS（ベイズ不確実性）・Zheng2025_PIDG（単眼動画対応）であり、ロボット操作文脈ではZheng2025_PhysTwin・Zhang2025_Real2SimSoft・Chen2026_EMPM・Huang2026_SoMAが3DGSをデジタルツインのレンダリング層として採用した。

**Building Block 3: ベイズ推定とハイブリッド最適化 (Bayesian Inference & Hybrid Optimization)**

決定論的な勾配降下だけでは局所最適やノイズに対して脆弱なため、グローバル探索とローカル精緻化を組み合わせるハイブリッド戦略が重要な基盤として確立されている。Yoon2025_RealtoSimClothはベイズ最適化 (Bayesian Optimization; BO)＋勾配降下で4パラメータを同定し、Li2024_BayesianDiffPhysicsは変分推論で空間的不均質性を捉えた。Lin2024_AdaptiGraphはBO/共分散行列適応進化戦略 (Covariance Matrix Adaptation Evolution Strategy; CMA-ES) によるオンライン逆最適化を展開時に実行し、Li2025_PhysGSはDirichlet-Categorical事前分布と正規-逆ガンマ事前分布による閉形式事後推定で質量22.8%・硬度61.2%の精度改善を達成した。

**Building Block 4: sim-to-realドメインランダム化と残差補正 (Domain Randomization & Residual Correction)**

Matas2018_SimtoRealは深層決定論的方策勾配法 (Deep Deterministic Policy Gradient; DDPG) への9改良とドメインランダム化の組み合わせでゼロショット転移を初めて実証し、Zhao2025_StressGuidedRLは内部応力ペナルティによる穏やかな操作の学習と転移を示した。Scheikl2023_RealtoSimはChamfer距離ベースの残差写像とオンライン剛性最適化の併用で手術組織の精密操作を実現した。Huang2023_DERはDERモデルの高精度化によりリアルデータ不要のゼロショット転移（76.7%成功率）を達成した。

**Building Block 5: ポイントクラウド・粒子系の観測モデリング (Point Cloud / Particle Observation)**

Yang2024_DPSIはノイズのある実ポイントクラウドに対してChamfer+EMD損失を直接適用し、Li2023_PACNeRFはニューラル輝度場 (Neural Radiance Field; NeRF) のボクセル表現からMPM粒子への変換器を導入した。DiPac2024_DifferentiableParticlesは単一の粒子ベースフレームワークでロープ・布・粒状体・液体を統一的に扱い、Shi2025_PhysWorldはMPMデジタルツインから合成データを生成してGNNワールドモデルを47倍高速化した。

---

### Progress（解決済み問題の軌跡）

**Phase 1 (2018–2020): 基礎の確立**

この時期の最大の達成は、深層強化学習によるゼロショットsim-to-real転移の実証である。Matas2018_SimtoRealはドメインランダム化を変形物体操作に初めて適用した。物理シミュレーション基盤ではHu2020_DiffTaichiが微分可能物理シミュレータのAD実装を確立し、現代の微分可能シミュレーション研究の礎を作った。Jatavallabhula2021_gradSim（2020年提出）は3D監督なしにビデオから物理属性をバックプロパゲートする統合微分グラフを提案した。ArriaolaRios2020_ModelingReviewはこの時期の知識を整理し、「ヤング率・ポアソン比の推定は未解決問題」と明示的に指摘した。

**Phase 2 (2021–2023): 微分可能シミュレーションの成熟とベンチマーク整備**

2021年から2023年にかけて、微分可能シミュレーションの能力が急速に拡大した。Huang2021_PlasticineLab は弾塑性MPMの微分可能化とVon Mises降伏を実現しベンチマークを整備した。Li2023_PACNeRFは形状事前知識不要の幾何+物理同時推定という大きな進歩を実現し、Wi2023_VIRDOppは視触覚融合による変形状態推定の精度を向上させた。DLO分野ではHuang2023_DERがDERモデルによる動的ワイヤ操作のゼロショット転移（76.7%成功率）を達成し、Gu2023_SurveyDeformableはこの時期の150件超の研究を体系化した。

**Phase 3 (2024–2026): 現在のフロンティア**

現在の最前線は「3DGSと物理演算の統合」「リアルタイムオンライン適応」「不確実性の定量化」という三方向に展開している。3DGS統合ではXie2023_PhysGaussianの先駆的提案を受けて、Liu2024_Physics3D・Wang2025_OmniPhysGS・Li2025_PhysGS・Zheng2025_PIDGが相次いで登場した。ロボット操作への直接接続ではZhang2025_Real2SimSoftがPearson r>0.9の政策評価相関を達成し、Chen2026_EMPMがオンライン準静的適応でリアルタイム補正を実現した。触覚センシングではLloyd2024_YoungModulusが285物体にわたって74.2%の精度で5桁の範囲をカバーするヤング率推定を初めて達成した。

---

### Gap（構造的な未解決問題）

**Gap 1: 接触・不連続性下での勾配品質の劣化**

接触イベントや材料の断裂・分離が生じる場面では、微分可能シミュレーションの勾配が信頼できなくなるという問題が複数の論文で繰り返し指摘されている。Hu2020_DiffTaichiは接触不連続での誤解な勾配を明示し、Huang2021_PlasticineLab は多段タスクでの離着接による失敗を報告し、Liu2024_SoftMACは積層布や非多様体形状への非適用性を認めている。Yang2024_DPSIは鞍点問題として、Yang2025_DDBot は局所最適問題として同じ現象の別側面を報告している。この構造的欠陥は現在の全ての微分可能シミュレーション手法に共通する未解決問題である。

**Gap 2: オクルージョン下での観測・追跡の信頼性**

変形物体が自己接触したり他の物体に隠蔽されたりする場合、ポイントクラウドや粒子追跡の品質が著しく低下する。Chen2026_EMPMは大変形とオクルージョン下での追跡品質劣化を認め、DiPac2024_DifferentiableParticlesはオクルージョン下での粒子取得失敗を制限として挙げ、Huang2026_SoMAとLin2024_AdaptiGraphも重度オクルージョンでの性能劣化を報告している。AbouChakra2024_EmbodiedGSはロープの小さな画素フットプリントを問題として指摘した。

**Gap 3: 空間的不均質性と異方性の表現**

実際の変形物体（複合材・生体組織・複数材料の布）は空間的に不均質でかつ異方性を持つが、多くの手法は均質等方性を仮定している。Li2024_BayesianDiffPhysicsは空間変化するパラメータのベイズ推定を提案したが布の座屈モデリングを除外し、Zheng2024_DiffCPのAEPモデルは異方性対応を主な貢献として掲げているが計算コストが高い。Scheikl2023_RealtoSimは手術組織の異方性を「捉えられない」と明示した。不均質・異方的なパラメータ分布を効率よく推定するスケーラブルな手法は未確立のままである。

**Gap 4: 実ロボット実験でのリアルタイム性と精度の両立**

Zheng2025_PIDGは数時間から数日の計算時間を要し、Scheikl2023_RealtoSimは1ステップあたり0.9–2.6秒かかりリアルタイム制御不能であり、Li2024_BayesianDiffPhysicsは後ろ向きMPMのメモリ要求を制限として挙げている。高速化のためにニューラルダイナミクス（Lin2024_AdaptiGraph・Huang2026_SoMA）や春-質点（Zheng2025_PhysTwin）が使われるが、物理的解釈可能性と汎化性能が犠牲になる。精度・速度・汎用性の三角形トレードオフは、いかなる現行手法によっても同時には解消されていない。

**Gap 5: 推定精度とロボット制御性能の定量的対応関係**

物理パラメータの推定誤差がロボットタスクの成功率にどう影響するかという定量的な関係は、ほとんどの論文で明示されていない。Zhang2025_Real2SimSoftはPearson r>0.9を示したが3タスクに限定され、Patni2024_OnlineElasticityは装置間誤差の定量化に留まり制御への影響は示していない。「どの程度の推定誤差まで許容できるか」という制御上のトレランス解析が欠如しており、これはロボット設計への実用的応用を阻む根本的なギャップである。

---

### Seed（研究提案）

#### Seed 1: 接触不連続を跨ぐ物性推定のための非滑らか微分可能シミュレーション

**背景**: Gap 1が示す通り、微分可能MPM・FEMは接触・断裂・剥離イベント付近で勾配が不正確になる。このため複数回の接触を含む操作（把持→変形→解放）からパラメータを同定しようとすると最適化が発散する。

**提案**: Moreau-Yosida正則化や Clarke劣微分を用いた非滑らか微分可能シミュレーションフレームワークを構築し、接触不連続点での正確な劣勾配計算を実現する。具体的にはDiffTaichi（Hu2020）の接触モデルをIncremental Potential Contact（IPC）へ置き換え、接触フォースの陰的微分を計算する。評価はPlasticineLab多段タスク（Huang2021で失敗が報告された離着接タスク）での物性回復精度を基準とする。

**新規性**: Yang2024_DPSIは鞍点問題を指摘しながら解決策を示さず、DiffTactile（Chen2024）はFEMをベースにするが接触勾配の一般的解決策は未提示。非滑らか微分可能シミュレーションを実ロボット物性推定に適用した例は存在しない。

**実現可能性**: IPC実装（Li et al., ACM SIGGRAPH 2020）はすでにオープンソース化されており、JAX/PyTorchへの統合は2人の研究者で1年以内に達成可能と想定される。

---

#### Seed 2: 物性推定誤差がロボット制御性能に与える影響の体系的解析

**背景**: Gap 5が示す通り、「推定精度とタスク成功率の定量的対応関係」を体系的に調査した研究は存在しない。これは実用化のための設計基準が存在しないことを意味する。

**提案**: 布折り畳み・ロープ挿入・弾塑性食品把持の3タスクを対象に、ヤング率E・ポアソン比ν・摩擦係数μについて意図的に推定誤差を注入したシミュレーション実験を行い、各パラメータの許容誤差域（タスク成功率95%を保つ誤差上限）を定量的にマッピングする。次にPhysTwin（Zheng2025）を用いた実ロボット実験で同じマッピングを実施し、sim-to-realでの感度の違いを分析する。

**新規性**: Patni2024_OnlineElasticityは装置間誤差を定量化したが制御への影響は示さず、Zhang2025_Real2SimSoftはPearson相関を示したが誤差注入実験は行っていない。感度解析によるトレランス設計は制御工学の標準手法だが変形物体操作への適用は未開拓。

**期待される貢献**: 「どのパラメータをどの精度で推定すれば十分か」という工学設計指針を初めて定量化し、物性推定器の設計優先度（例：Eの±20%誤差はタスク成功に許容されるがνの±5%誤差は不可）を明確にする。

---

#### Seed 3: 非均質・異方的変形物体の局所物性推定のためのマルチスケール3DGS-MPMフレームワーク

**背景**: Gap 3が示す通り、空間的不均質性と異方性を持つ実物体（複合材・食品・生体組織）への対応は未解決である。既存手法（DiffCP, BayesianDiffPhysics）は均質仮定を部分的に緩和するが、スケーラビリティと計算効率に課題がある。

**提案**: 3DGS表現の各ガウシアンに局所的な異方性構成テンソル（Transverse Isotropy の5パラメータ）を割り当て、Li2025_PhysGSのベイズ事前分布と組み合わせた空間変化型確率的物性マップを構築する。マクロスケール（シーンレベル）での3DGS観測とメゾスケール（材料パッチレベル）でのMPMシミュレーションを階層的に連結することで、局所物性の観測可能性を確保する。

**新規性**: OmniPhysGS（Wang2025）は12種の均質材料モデルを選択するが空間変化には対応していない。Li2025_PhysGSはベイズ推定を提供するが等方性を仮定している。異方性3DGS-MPMとベイズ不確実性推定の組み合わせは新規である。

**評価**: 異なる繊維方向を持つ複合材シートの把持・変形タスクで、推定した5パラメータ構成テンソルの精度と下流操作性能を評価する。

---

### RQ Answers

**RQ1**: 変形可能物体の物性推定に向けて、少なくとも五つの主要なアルゴリズム系統が並行して発展してきた。第一は微分可能MPM（DiffTaichi, PlasticineLab, PAC-NeRF, DPSI, DDBot, EMPM）であり、粒子ベースの材料点法を通じてヤング率・ポアソン比・密度・摩擦角などの連続パラメータを勾配降下で同定する。第二は3DGS統合物理（PhysGaussian, Physics3D, OmniPhysGS, PhysGS, PIDG, EmbodiedGS）であり、3Dガウシアンスプラッティングの表現力と物理シミュレーションを統合して視覚的リアリティと動態一致を同時に達成する。第三はバネ質点/FEMハイブリッド（PhysTwin, Real2SimSoft, ThinShellLab, DiffTactile）であり、布・デジタルツイン分野で活用される。第四は微分可能離散弾性ロッド（DER）と残差ニューラルネットワーク（Cheng2024_DEFORM, Huang2023_DER, Ying2024）であり、DLOの曲げ・ねじり剛性の同定に特化する。第五はプロパティ条件付きニューラルダイナミクス（AdaptiGraph, SoMA, PhysWorld, VIRDO++）であり、物理モデルを陽に持たずに観測から変形動態を学習する。実際には3DGS＋MPM、ベイズ推論＋勾配降下、物理シミュレーション＋残差ニューラルネットなど複数の組み合わせが主流になりつつある。

**RQ2**: 推定された物理特性を実際のロボット操作に活用した事例は多数存在するが、達成されたタスクの種類と精度の報告様式は大きく異なる。DLO操作ではHuang2023_DERが動的ワイヤ操作で76.7%の実環境成功率を達成し、Li2024_DLOFlexibilityは柔軟性条件付きポリシーでの挿入タスクを実証した。布操作ではMatas2018_SimtoRealがゼロショット転移を実証し、Yoon2025_RealtoSimClothがハイブリッドBO＋勾配降下で4パラメータを正確に回復した。デジタルツイン文脈ではZhang2025_Real2SimSoftが3タスクのロボット政策評価でPearson r>0.9を達成した。弾塑性材料操作ではYang2024_DPSIとChen2026_EMPMが実点群との照合でパラメータ同定と操作を結合した。触覚による絶対値ヤング率推定ではLloyd2024_YoungModulusが285物体・5桁範囲で74.2%以内の精度を示した。全体として「推定精度とタスク成功率」の明示的な対応関係を定量的に報告している論文は少なく、標準ベンチマークの欠如が比較可能性を阻んでいる。

**RQ3**: sim-to-realギャップへの対処戦略は複数の方向に分化している。最も基礎的な戦略はドメインランダム化（Matas2018, Zhao2025）であり、剛性・摩擦・外観パラメータを広範囲にランダム化することで実環境変動への頑健性を確保する。より精緻な戦略はオンライン適応と残差補正であり、Scheikl2023_RealtoSimは残差写像とオンライン剛性最適化の両方を組み合わせることで単独より高い精度を実現した。物理モデルの高精度化ではHuang2023_DERがDERの精度を高めることでリアルデータ不要の転移を達成した。推定精度がロボット制御品質に与える影響の定量的分析は、Zhang2025_Real2SimSoftのPearson r>0.9が最も包括的であるが、限定的な3タスクでの評価に留まる。「パラメータ推定誤差がタスク成功率にどの程度の閾値まで許容されるか」を体系的に調査した研究は存在しない。

**RQ4**: 複数の論文が繰り返し指摘する未解決課題は以下の通りである。第一に、接触不連続・大変形・破断を伴う場面での微分可能シミュレーションの信頼性が根本的に限界に達しており、いかなる手法も一般的な解決策を提示できていない。第二に、オクルージョン・自己接触下での3D観測の信頼性が課題であり、現行の点群・3DGSベース手法は重度の遮蔽に脆弱である。第三に、空間的不均質・異方的な材料のスケーラブルな推定が未達成であり、実際の生体組織・複合材料への適用には根本的な表現力の拡張が必要である。第四に、リアルタイム性と推定精度の両立が現行手法の最大のボトルネックである。第五に、推定精度と操作性能の定量的対応関係が体系的に未調査であり、エンジニアリング上の設計基準が存在しない。ArriaolaRios2020が2020年時点で指摘した「新規材料に対するEとνの推定は未解決」という根本的課題が、2026年現在もなお完全には解決されていないことは注目に値する。

---

### Quantitative Trends

#### 発表年別論文数

| 年 | 論文数 | 主な論文 |
|---|---|---|
| 2018 | 1 | Matas2018_SimtoReal |
| 2020 | 2 | Hu2020_DiffTaichi, ArriaolaRios2020 |
| 2021 | 3 | Huang2021_PlasticineLab, Jatavallabhula2021_gradSim, Lin2021_SoftGym |
| 2023 | 5 | Li2023_PACNeRF, Xie2023_PhysGaussian, Wi2023_VIRDOpp, Huang2023_DER, Scheikl2023 |
| 2024 | 15 | Yang2024_DPSI, Wang2024_ThinShellLab, Zheng2024_DiffCP, Li2024_BayesianDiffPhysics, Li2024_DLOFlexibility, Cheng2024_DEFORM, Ying2024, Patni2024, Lloyd2024, Chen2024_PropriocepEstimation, AbouChakra2024, Lin2024_AdaptiGraph, DiPac2024, Liu2024_SoftMAC, Chen2024_DiffTactile |
| 2025 | 12 | Wang2025_OmniPhysGS, Li2025_PhysGS, Zheng2025_PIDG, Zheng2025_PhysTwin, Zhang2025, Shi2025, Yang2025_DDBot, Zhao2025, Yoon2025, Gu2023_Survey (accepted 2023), Liu2024_Physics3D (preprint), Cai2024_GIC (NeurIPS 2024) |
| 2026 | 3 | Chen2026_EMPM, Huang2026_SoMA, Gu2023 (publication year note) |

2024年が最大のピーク（約15件）であり、特に3DGS関連・ベイズ的アプローチ・DLO関連の研究が集中した。

#### 主要会場別（上位）

| 会場 | 論文数 |
|---|---|
| ICLR | 6 (DiffTaichi, PlasticineLab, gradSim, ThinShellLab, DiffTactile, PAC-NeRF) |
| ICRA / RA-L | 4 (DiffCP, DLOFlexibility, PropriocepEstimation, SoftMAC≈IROS) |
| CoRL | 4 (Matas2018, SoftGym, VIRDO++, EmbodiedGS, DEFORM) |
| NeurIPS | 2 (GIC-Oral, Physics3D-preprint) |
| CVPR / ICCV | 2 (PhysGaussian, PhysTwin) |
| RSS | 1 (AdaptiGraph) |
| WAFR | 1 (DeformGS) |
| IEEE T-RO / IJRR | 2 (DDBot, DPSI) |
| Journals | 4 (Arriola-Rios, DiffCP-RAL, Patni-IJAMT, Yoon-JCDE) |

#### カテゴリ別

| カテゴリ | 件数 |
|---|---|
| シミュレーションのみ | 8 |
| 実ロボットデモのみ | 6 |
| シミュレーション＋実ロボット | 22 |
| 調査・ベンチマーク | 5 |

実ロボット実験を含む論文が全体の60%超を占め、特に2024年以降は純粋なシミュレーション研究よりも実環境実証を伴う研究が主流となっている。


## Paper Catalogue

### Category A: Differentiable Physics / MPM

**A1. Yang2024_DPSI**  
Xintong Yang, Ze Ji, Yu-Kun Lai. "Differentiable Physics-based System Identification for Robotic Manipulation of Elastoplastic Materials." *International Journal of Robotics Research*, 2025.  
arXiv: 2411.00554 | DOI: 10.1177/02783649251334661  
- **thesis**: 弾塑性材料（ヤング率・ポアソン比・降伏応力・摩擦）は最小限の実ロボット接触からnoisy点群に対するChamfer+EMD損失を通じた微分可能移動最小二乗MPM (Moving Least Squares MPM; MLS-MPM) で信頼性高く同定できる
- **core**: DiffTaiChiによる微分可能MLS-MPM; Chamfer距離とEarth Mover's Distance損失の組み合わせ
- **diff**: GradSim・PAC-NeRFが合成完全映像を前提とするのに対し、ノイズのある実点群に直接適用
- **limit**: 鞍点問題; 接触領域のシャープな変形; 変位後の粒子浮遊

**A2. Chen2026_EMPM**  
Yunuo Chen, Yafei Hu, Lingfeng Sun, et al. "EMPM: Embodied MPM for Modeling and Simulation of Deformable Objects." *arXiv*, 2026.  
arXiv: 2601.17251  
- **thesis**: マルチビューRGBD再構成とオンライン感覚フィードバックを組み合わせた微分可能MPMはバネ質点系より複雑な変形物体のモデリングに優れる
- **core**: オフライン微分可能MPM最適化（NVIDIA Warp）＋EとνのオンラインQuasi-Static適応
- **diff**: PhysTwinのバネ質点に対し弾塑性・破断での精度優位; 3DGSによる測光レンダリングを追加
- **limit**: オクルージョン・大変形下でのポイント追跡劣化

**A3. Li2023_PACNeRF**  
Xuan Li, Yi-Ling Qiao, Peter Yichen Chen, et al. "PAC-NeRF: Physics Augmented Continuum Neural Radiance Fields for Geometry-Agnostic System Identification." *ICLR 2023 Spotlight*.  
arXiv: 2303.05512  
- **thesis**: 形状事前知識なしにマルチビュー映像から幾何形状と物理パラメータを同時推定できる
- **core**: Eulerian格子NeRF＋Lagrangian MPM粒子をparticle-grid interconverterで連結した微分可能ハイブリッド表現
- **diff**: GradSim・DiffTaichiが既知形状を前提とするのを排除; NeRFより~100倍高速レンダリング
- **limit**: キャリブレーション済みカメラ必須; 薄板（布）不可; 構成モデル種の事前知識必要

**A4. Cai2024_GIC**  
Junhao Cai, Yuji Yang, Weihao Yuan, et al. "GIC: Gaussian-Informed Continuum for Physical Property Identification and Simulation." *NeurIPS 2024 Oral*.  
arXiv: 2406.14927 | DOI: 10.5555/3737916.3740304  
- **thesis**: 3DGS再構成の明示的な幾何学的監督を微分可能MPMシミュレーションに与えることで物性同定精度が向上する
- **core**: 動態分離型3DGS再構成→粗から細への密度場生成→Gaussianマスク監督付き微分可能MPMの3段パイプライン
- **diff**: PAC-NeRF（RGB監督）の大変形でのテクスチャ歪みを排除; 明示的表面のChamfer距離＋マスクL1損失
- **limit**: 連続体力学を仮定; 既知カメラ姿勢と構成モデル種の事前知識必要

**A5. Jatavallabhula2021_gradSim**  
Krishna Murthy Jatavallabhula, Miles Macklin, et al. "gradSim: Differentiable simulation for system identification and visuomotor control." *ICLR 2021*.  
arXiv: 2104.02646  
- **thesis**: 物理シミュレーションと微分可能レンダリングの統合微分グラフにより3D監督なしにビデオピクセルから物理属性へのバックプロパゲーションが可能
- **core**: ダイナミクス（剛体・変形体・布）と画像生成（SoftRas/DIB-R）を跨ぐ統一微分計算グラフ
- **diff**: ブラックボックスニューラル（解釈不可）・ホワイトボックス物理（3D監督必要）に対し、3D監督なしで質量・摩擦・弾性を回復
- **limit**: モデル仮定違反に敏感; sim-to-realギャップは取り扱わない

**A6. Hu2020_DiffTaichi**  
Yuanming Hu, Luke Anderson, Tzu-Mao Li, et al. "DiffTaichi: Differentiable Programming for Physical Simulation." *ICLR 2020*.  
arXiv: 1910.00935  
- **thesis**: 物理シミュレータはメガカーネル・命令型並列性・任意インデックスを尊重した専用ADを必要とする
- **core**: イントラカーネル微分のソースコード変換＋エンドツーエンドバックプロパゲーションのテープによる二段階自動微分 (Automatic Differentiation; AD)
- **diff**: TF/PyTorch/JAX（GPU kernel起動過多）と手書きCUDA（手動勾配誘導）の中間を自動化
- **limit**: 接触不連続での誤導勾配; 平坦な損失ランドスケープと局所最小値

**A7. Huang2021_PlasticineLab**  
Zhiao Huang, Yuanming Hu, Tao Du, et al. "PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics." *ICLR 2021*.  
arXiv: 2104.03311  
- **thesis**: 微分可能弾塑性シミュレーションは勾配ベース最適化でRLでは不可能なソフトボディ操作タスクを解けるが、多段タスクには失敗する
- **core**: 微分可能MLS-MPM＋Von Mises降伏（微分可能特異値分解 (Singular Value Decomposition; SVD)）＋ソフト化接触モデル; 10シナリオ50設定のベンチマーク
- **diff**: ChainQueen・DiffTaichiに塑性と包括的タスク評価を追加
- **limit**: 離着接を伴う多段タスクでの失敗; 初期値感度; sim-to-real未探索

**A8. Yang2025_DDBot**  
Xintong Yang, Minglun Wei, Yu-Kun Lai, Ze Ji. "DDBot: Differentiable Physics-based Digging Robot for Unknown Granular Materials." *IEEE Transactions on Robotics*, 2025.  
arXiv: 2510.17335 | DOI: 10.1109/TRO.2025.3636815  
- **thesis**: Drucker-Prager塑性付き微分可能MLS-MPMにより未知粒状材料のE・ν・密度・摩擦角を同時回復し、少サンプルで掘削スキルを最適化できる
- **core**: 完全微分可能MLS-MPM（サン・ブナン・キルヒホッフ弾性 (Saint Venant-Kirchhoff; StVK) ＋Drucker-Prager塑性）＋勾配安定化（クリッピング・ダイナミックスケーリング・正規化）＋直線探索
- **diff**: グラフニューラルネットワーク (Graph Neural Network; GNN)・CMA-MAE・深層強化学習 (Reinforcement Learning; RL) に対し微分可能物理で4パラメータを少サンプルで回復
- **limit**: 小規模高精度掘削に限定; 局所最適

**A9. Liu2024_SoftMAC**  
Min Liu, Gang Yang, Siyuan Luo, Lin Shao. "SoftMAC: Differentiable Soft Body Simulation with Forecast-based Contact Model and Two-way Coupling." *IROS 2024*.  
arXiv: 2312.03297 | DOI: 10.1109/IROS58592.2024.10801308  
- **thesis**: ソフトボディ操作の有効な微分可能シミュレーションには軟体・剛体・布の統一双方向結合が必要
- **core**: 先読み速度計算に基づくforecast-based接触モデル＋非体積布メッシュへの局所SDF再構成
- **diff**: PlasticineLab・FluidLab（一方向結合のみ）に対し初の微分可能双方向ソフト-剛体・ソフト-布結合
- **limit**: 積層布と非多様体形状への非適用; forecast接触の計算オーバーヘッド

---

### Category B: 3DGS + Physics

**B1. Xie2023_PhysGaussian**  
Tianyi Xie, Zeshun Zong, Yuxing Qiu, et al. "PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics." *CVPR 2024*.  
arXiv: 2311.12198 | DOI: 10.1109/CVPR52733.2024.00420  
- **thesis**: 3Dガウシアン核はレンダリング基本単位と物理シミュレーション離散化を同時に担えるWS2原理が成立する
- **core**: 各ガウシアンに変形勾配・応力属性を付加しMPM連続体力学で時間発展; 局所アフィン変換により変形後もガウシアン性を保持
- **diff**: NeRF編集手法（メッシュ抽出と物理変形の乖離）に対し中間幾何表現なしに物理拘束を直接適用
- **limit**: 影の発展を未モデル化; 一点求積が個々の楕円体サイズを不十分に表現

**B2. Liu2024_Physics3D**  
Fangfu Liu, Hanyang Wang, Shunyu Yao, et al. "Physics3D: Learning Physical Properties of 3D Gaussians via Video Diffusion." *arXiv preprint*, 2024.  
arXiv: 2406.04338  
- **thesis**: ビデオ拡散モデルの運動事前分布を蒸留することで実計測なしに3DGSの質量・ラメ定数・粘性を推定できる
- **core**: 弾性成分と粘弾性成分を独立分解する粘弾性MPM; Stable Video Diffusionへのスコア蒸留サンプリング (Score Distillation Sampling; SDS)
- **diff**: PhysDreamer（弾性のみ）・PhysGaussian（低周波不自然挙動）に対し弾性＋粘性を同時モデル化
- **limit**: 絡み合いが多いシーンでは手動介入が必要

**B3. Wang2025_OmniPhysGS**  
Yuchen Lin, Chenguo Lin, Jianjin Xu, Yadong Mu. "OmniPhysGS: 3D Constitutive Gaussians for General Physics-Based Dynamics Generation." *ICLR 2025*.  
arXiv: 2501.18982  
- **thesis**: 12専門家構成モデルのアンサンブルから自動選択することで手動材料指定なしに異種物理動態を生成できる
- **core**: 物理誘導ニューラルネット (Neural Network; NN) が12構成モデルをGaussianごとに選択・ブレンド; ビデオ拡散モデルへのSDS; グループ化マルチバッチ最適化
- **diff**: PhysGaussian・PhysDreamer（手動チューニング必要）・Physics3D（単一固定構成モデル）に対し材料選択自動化
- **limit**: 代表的材料のみカバー; シーンごとの最適化が遅い

**B4. Li2025_PhysGS**  
Xutao Li, Yiming Ji, et al. "PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation." *arXiv*, 2025.  
arXiv: 2511.18570  
- **thesis**: 3DGSのベイズ推論により多様な実物体の物性（摩擦・剛性・硬度・密度・質量）を原理的な不確実性定量化とともに推定できる
- **core**: Dirichlet-Categorical材料ラベルモデル＋Normal-Inverse-Gamma連続物性事前分布; 閉形式事後更新; 視覚言語モデル (Vision-Language Model; VLM) 事前分布との融合
- **diff**: NeRF2Physics（決定論的点推定）に対し校正済み不確実性を提供; 質量22.8%・硬度61.2%・摩擦18.1%の誤差低減
- **limit**: セグメント・エニシング・モデル (Segment Anything Model; SAM) のセグメンテーション品質に敏感; 雑然とした屋外シーンでノイズが増加

**B5. Zheng2025_PIDG**  
Zhenwei Shi, Yurui Chen, et al. "Physics-Informed Deformable Gaussian Splatting." *AAAI 2026*.  
arXiv: 2511.06299  
- **thesis**: 各ガウシアンにCauchy運動量方程式を課し光流れとの整合をLagrangian的に取ることで単眼動画から物理整合性のある動態再構成が可能
- **core**: 4D分解ハッシュエンコーディング（メモリO(n^3)）; Cauchy Momentum Residual損失＋カメラ補正光流れとのLagrangian整合損失
- **diff**: GaussianFlow・MotionGS（剛体変換のみ）に対し連続体力学を強制; マルチビュー入力不要
- **limit**: 数時間から数日の最適化; 非線形弾塑性・粘弾性の不完全なカバレッジ

**B6. AbouChakra2024_EmbodiedGS**  
Jad Abou-Chakra, Krishan Rana, Feras Dayoub, Niko Sünderhauf. "Physically Embodied Gaussian Splatting: A Realtime Correctable World Model for Robotics." *CoRL 2024*.  
arXiv: 2406.10788  
- **thesis**: PBD物理予測と3DGSとを継続的な視覚力補正でリアルタイム（30Hz）閉ループ接続することでロボティクス向け補正可能なワールドモデルを構築できる
- **core**: 粒子-Gaussianデュアル表現; 位置ベースダイナミクス (Position-Based Dynamics; PBD) が将来状態を予測; Adam最適化測光損失による視覚力でリアル追従
- **diff**: PBD＋3DGSを組み合わせたリアルタイム閉ループ補正は先行研究なし
- **limit**: ロープの小画素フットプリントで補正力が不安定; 対称・無模様物体での定常追跡誤差

---

### Category C: Spring-Mass / Hybrid

**C1. Zheng2025_PhysTwin**  
Hanxiao Jiang, Hao-Yu Hsu, Kaifeng Zhang, et al. "PhysTwin: Physics-Informed Reconstruction and Simulation of Deformable Objects from Videos." *arXiv*, 2025.  
arXiv: 2503.17973  
- **thesis**: 疎なマルチビューRGBD映像の単一インタラクションシーケンスからバネ質点物理・生成形状事前分布・3DGSを組み合わせることでフォトリアリスティックで物理的に正確なデジタルツインを再構成できる
- **core**: 非微分可能トポロジパラメータへの零次最適化＋バネ質点シミュレータ内の連続物理パラメータへの勾配ベース精緻化の階層的スパース-密度最適化
- **diff**: Spring-Gaus（密な視点必要）・GS-Dynamics（大規模訓練データ必要）に対し多様な変形物体への単一インタラクションでの汎化
- **limit**: 3台のRGBDカメラを使用; より疎な観測への拡張が今後の課題

**C2. Zhang2025_Real2SimSoft**  
Kaifeng Zhang, Shuo Sha, Hanxiao Jiang, et al. "Real-to-Sim Robot Policy Evaluation with Gaussian Splatting Simulation of Soft-Body Interactions." *arXiv*, 2025.  
arXiv: 2511.04665  
- **thesis**: 3DGSレンダリングとバネ質点デジタルツインで構築したシミュレートされたロールアウトは実世界実行性能と強い相関（r>0.9）を持ち政策評価のプロキシとして機能する
- **core**: PhysTwinフレームワークによるバネ質点パラメータ最適化＋NVIDIA Warpエンジン＋線形ブレンドスキニング (Linear Blend Skinning; LBS); Pearson r>0.9（IsaacLab: r=0.237-0.649と比較）
- **diff**: SIMPLER・RobotArena∞・Ctrl-World・Real-is-Sim（剛体のみ）に対しr>0.9の変形物体シミュレーション
- **limit**: 残留外観・ダイナミクス不一致; 3タスク1ロボットプラットフォームへの評価限定

**C3. Shi2025_PhysWorld**  
Hao Shi et al. "PhysWorld: From Real Videos to World Models of Deformable Objects via Physics-Aware Demonstration Synthesis." *arXiv*, 2025.  
arXiv: 2510.21447  
- **thesis**: 短い実映像からMPMパラメータを最適化し多様なデモを合成することでGNNワールドモデルを47倍高速化しながら競争力ある精度を維持できる
- **core**: MPMデジタルツイン構築（VLM支援構成モデル選択＋大域-局所物性最適化）→多様デモ合成→空間変化物性埋め込み付きGNN
- **diff**: GNN（大規模実データ必要）・PhysTwin（計算コスト大）に対しシミュレーションを合成データ生成器として活用
- **limit**: シンプルなシミュレータと複雑な現実の間のドメインギャップ; 長期ロールアウトでの誤差蓄積

---

### Category D: Cloth / Thin-Shell

**D1. Wang2024_ThinShellLab**  
Yian Wang, Juntian Zheng, Zhehuan Chen, et al. "Thin-Shell Object Manipulations With Differentiable Physics Simulations." *ICLR 2024 Spotlight*.  
arXiv: 2404.00451  
- **thesis**: 薄板操作には曲げ剛性と塑性を捉える微分可能シミュレーションが必要; CMA-ES＋勾配降下のハイブリッド戦略が必要
- **core**: Kirchhoff-Loveシェル理論＋IPC摩擦＋微分可能曲げ-塑性; 実触覚データからE・ν・曲げ剛性を同定
- **diff**: SoftGym・DaxBench（曲げ剛性なし）・DiffCloth・C-IPC（操作タスクスイートなし）に対し塑性サポートと包括的ベンチマークを追加
- **limit**: 視覚情報なしの触覚・力センサのみ; 接触モデル不一致による残差ギャップ; 開ループ制御のみ

**D2. Zheng2024_DiffCP**  
Dongzhe Zheng, Siqiong Yao, Wenqiang Xu, Cewu Lu. "Differentiable Cloth Parameter Identification and State Estimation in Manipulation." *IEEE RA-L*, 2024.  
arXiv: 2311.05141 | DOI: 10.1109/LRA.2024.3355731  
- **thesis**: 布操作は物理パラメータ（E・ν・せん断・接触剛性）と布状態をRGB-Dから同時回復する必要がある
- **core**: MPM＋異方性弾塑性 (Anisotropic Elasto-Plastic; AEP) 構成モデルを用いたDiffCP微分パイプライン; 幾何分散最小化による勾配降下でパラメータと姿勢を同時最適化
- **diff**: 等方性Neo-Hookean布手法に対しAEPで異方性対応; 接触を陰的に処理し関節ポーズ＋パラメータ最適化
- **limit**: センサ不精度による実-シム差異; 微分可能MPMの高メモリ要求

**D3. Li2024_BayesianDiffPhysics**  
D. Li et al. "Bayesian Differentiable Physics for Cloth Digitalization." *arXiv*, 2024.  
arXiv: 2402.17664  
- **thesis**: 正確な布デジタル複製には標準化されたCusickドレープ試験と空間的に不均質なパラメータ分布とパラメータ不確実性を捉えるベイズ微分物理が必要
- **core**: 有限要素メッシュノード上の空間変化布パラメータへの変分推論; 標準Cusickドレープ試験画像から確率的パラメータ推定
- **diff**: 均質布を仮定した決定論的微分物理手法に対し空間不均質性＋ベイズ不確実性を同時表現
- **limit**: 物理の事前知識が必要; 座屈のような複雑な動態は未モデル化

**D4. Yoon2025_RealtoSimCloth**  
K. Yoon, S.-C. Lim. "Real-to-Sim High-Resolution Cloth Modeling: Physical Parameter Optimization Using Particle-Based Simulation." *J. Comput. Design Eng.*, 2025.  
DOI: 10.1093/jcde/qwae069  
- **thesis**: BO＋勾配降下のハイブリッド最適化により実ロボット操作データから高解像度粒子ベース布シミュレーションの4物理パラメータを正確に回復し布種・スケール・未見タスクへ汎化できる
- **core**: 80×80ノード粒子メッシュ; BO（大域探索）＋勾配降下（局所精緻化）による4パラメータ同時最適化
- **diff**: データ駆動（大規模ラベル必要）・物理誘導（視覚忠実度低）・単一タスク推定（汎化不可）に対しハイブリッド最適化と物理ベースを組み合わせ
- **limit**: 細かいしわの予測が困難; 高い計算コスト

---

### Category E: Deformable Linear Objects (DLO)

**E1. Li2024_DLOFlexibility**  
Mingen Li, Changhyun Choi. "Learning for Deformable Linear Object Insertion Leveraging Flexibility Estimation from Visual Cues." *ICRA 2024*.  
arXiv: 2410.23428 | DOI: 10.1109/ICRA57147.2024.10610419  
- **thesis**: DLO挿入には各物体の柔軟性に条件付けられたタスクポリシーが必要; GNNによる曲率ベース柔軟性推定で材料を跨いだ汎化が可能
- **core**: シミュレーションデータ訓練のGNN柔軟性推定器→柔軟性条件付きソフト・アクター・クリティック (Soft Actor-Critic; SAC) ポリシー（運動プリミティブ付き）; 追加ポリシー訓練なしのsim-to-real
- **diff**: 剛体モデルや実データを必要とする先行DLO手法（Lv, Scheikl）に対しデモデータ不要で材料適応
- **limit**: 高い挿入角度での成功率急落; センサノイズ; 平面挿入仮定

**E2. Huang2023_DER**  
Z. Huang et al. "Accurate Simulation and Parameter Identification of Deformable Linear Objects using Discrete Elastic Rods." *IROS 2025*.  
arXiv: 2310.00911 | DOI: 10.1109/IROS60139.2025.11247160  
- **thesis**: 物理的に正確なDER（曲げ・ねじり剛性を個別にパラメータ化）ベースのシミュレーションにより実ロボットデータ不要のゼロショット動的ワイヤ操作転移が可能
- **core**: DERをMuJoCoシミュレータに統合＋近位方策最適化 (Proximal Policy Optimization; PPO) によるポリシー学習; 2mワイヤのフリック操作で76.7%の実成功率
- **diff**: 実訓練データに依存する先行動的DLO手法に対しシミュレーション精度向上でデータ不要の転移
- **limit**: 関節コントローラの軌跡忠実度ギャップ; ワイヤパラメータ変動に敏感（細いワイヤで10%成功率）; 摩擦モデリング不完全

**E3. Cheng2024_DEFORM**  
Z. Cheng et al. "Differentiable Discrete Elastic Rods for Real-Time Modeling of Deformable Linear Objects." *CoRL 2024*.  
arXiv: 2406.05931  
- **thesis**: 微分可能DERと誤差を補正する残差ニューラルネットの組み合わせにより精度-効率トレードオフを克服したリアルタイムDLO予測が可能
- **core**: PyTorchによるDifferentiable DER（DDER）＋物理予測をショートカット接続とした残差DNN; 運動量保存非伸長性拘束
- **diff**: 純粋DER（遅い）・純粋GNN（大規模データ＋長期失敗）に対し物理＋学習の残差補正で橋渡し
- **limit**: DLO自己接触の予測不可; マルチブランチ構造未対応

**E4. Ying2024_ObstacleAvoidanceDLO**  
C. Ying, K. Yamazaki. "Obstacle Avoidance Shape Control of DLOs with Online Parameters Adaptation Based on Differentiable Simulation." *ROBOMECH Journal*, 2024.  
DOI: 10.1186/s40648-024-00283-1  
- **thesis**: 微分可能シミュレーション＋モデル予測制御 (Model Predictive Control; MPC)＋オンラインパラメータ適応により事前訓練データなしで任意材料特性のDLOの障害物回避形状制御が可能
- **core**: 前向きシミュレーションと勾配バックプロパゲーションをサポートするDLOモデル; MPCループ内の行動予測ニューラルネット; オンライン剛性適応
- **diff**: 事前収集訓練データと手設計コントローラを必要とする学習ベース手法に対しオフラインデータ不要で障害物拘束を扱う
- **limit**: オンライン適応はsim-to-realギャップを完全には閉じない

---

### Category F: Tactile / Sensing

**F1. Patni2024_OnlineElasticity**  
Shubhan P. Patni, Pavel Stoudek, Hynek Chlup, Matej Hoffmann. "Online Elasticity Estimation and Material Sorting Using Standard Robot Grippers." *Int. J. Adv. Manuf. Technol.*, 2024.  
arXiv: 2401.08298 | DOI: 10.1007/s00170-024-13678-6  
- **thesis**: 標準的な平行グリッパは弾性・粘弾性による軟体物体識別は可能だが絶対ヤング率の信頼性ある回復はできない; 材料ソートには相対的識別で十分
- **core**: 2グリッパ＋手首F/Tセンサ vs 専門バイアクシャル圧縮装置の系統的比較; 線形応力-ひずみ近似＋Hunt-Crossley粘弾性モデル（R²=0.81）
- **diff**: カスタム計装グリッパや高価なFEM手法に対し標準ハードウェアでの初の多グリッパベンチマーク
- **limit**: 装置間で係数2の絶対誤差; 特定の発泡材料とグリッパ形状への限定

**F2. Lloyd2024_YoungModulus**  
J. Lloyd et al. "Learning Object Compliance via Young's Modulus from Single Grasps with Camera-Based Tactile Sensors." *arXiv*, 2024.  
arXiv: 2406.15304  
- **thesis**: Hertz接触理論の解析的推定値と触覚画像特徴を融合した多タワーNNにより単一把持で5桁の範囲にわたるヤング率推定が可能
- **core**: Hertz接触理論＋弾性力学に基づく解析推定値＋触覚画像特徴＋把持計測値を融合した多タワーNN; 285物体で74.2%（1オーダー以内）
- **diff**: Shore硬度（軟質のみ）・大規模言語モデル (Large Language Model; LLM)（二値識別）・純解析手法（幾何変動に脆弱）に対し触覚把持から材料を跨ぐヤング率推定を初めて実現
- **limit**: 剛体間（プラスチックvs金属）の識別が困難; Hertz球面接触仮定の誤差; センサ分解能の限界

**F3. Chen2024_PropriocepEstimation**  
Peter Yichen Chen, Chao Liu, et al. "Learning Object Properties Using Robot Proprioception via Differentiable Robot-Object Interaction." *ICRA 2025*.  
arXiv: 2410.03920 | DOI: 10.1109/ICRA55162.2025.11127955  
- **thesis**: 操作中のロボット固有受容反応（関節エンコーダ信号）は外部センサ・視覚なしに物体質量と弾性率を微分可能シミュレーションで同定するのに十分な情報を含む
- **core**: ロボット-物体接触ダイナミクスの微分可能シミュレーション; 標準関節位置軌跡からのバックプロパゲーションで質量・弾性率を同定
- **diff**: センサ固有・ビジョンベースの物体同定手法に対しロボット反応データのみを使用し外部計測ツール不要
- **limit**: 公開アブストラクトからは明示的制限は確認できず

**F4. Wi2023_VIRDOpp**  
Youngsun Wi, Andy Zeng, Pete Florence, Nima Fazeli. "VIRDO++: Real-World, Visuo-tactile Dynamics and Perception of Deformable Objects." *CoRL 2023*.  
arXiv: 2210.03701  
- **thesis**: 特権的接触情報なしの多モーダル視触覚ニューラル陰的表現により高忠実度変形状態推定と汎化が実現できる
- **core**: ニューラル陰的表現上の変形ダイナミクス＋特権的接触情報不要の確率的状態推定器
- **diff**: 前身のVIRDOが展開時に特権的接触情報を必要としたのに対し不要化; ダイナミクス予測モジュールを追加
- **limit**: 明示的制限は論文で定量化されていない

**F5. Chen2024_DiffTactile**  
S. Chen et al. "DiffTactile: A Physics-based Differentiable Tactile Simulator for Contact-Rich Robotic Manipulation." *ICLR 2024*.  
arXiv: 2403.08716  
- **thesis**: FEMベースの全微分可能触覚シミュレータがsim-to-realギャップを閉じながら勾配ベース軌跡最適化を可能にし、サンプリングベース・RLアプローチを凌駕する
- **core**: FEM（Neo-Hookean）弾性体＋MLS-MPM多材料＋PBDケーブル＋ペナルティ接触＋多層パーセプトロン (Multi-Layer Perceptron; MLP) 光学触覚レンダラーの全微分可能統合パイプライン
- **diff**: 先行触覚シミュレータ（ソフトボディダイナミクスなし）に対し多様な材料タイプへのシステム全体微分可能性
- **limit**: 逆方向微分が順方向の2倍遅い; 接触パラメータは同定値周辺のランダム化に依存

---

### Category G: Sim-to-Real / Task Application

**G1. Matas2018_SimtoReal**  
J. Matas, S. James, A. J. Davison. "Sim-to-Real Reinforcement Learning for Deformable Object Manipulation." *CoRL 2018*.  
arXiv: 1806.07851  
- **thesis**: ドメインランダム化を伴う深層RLにより布操作ポリシーをシミュレーションのみで学習し実ロボットへゼロショット転移できる
- **core**: 9改良統合DDPG（優先リプレイ・Nステップ・TD3・行動クローニング・補助予測）＋剛性・摩擦・外観のドメインランダム化
- **diff**: 変形物体操作への深層RL＋sim-to-realの初適用; 先行手法は明示的物理モデルや手設計ヒューリスティックに依存
- **limit**: 実布がシミュレーションより剛い; 過剰ランダム化が転移性能を低下; カメラ位置感度

**G2. Zhao2025_StressGuidedRL**  
Y. Zhao et al. "Sim-to-Real Gentle Manipulation of Deformable and Fragile Objects with Stress-Guided Reinforcement Learning." *arXiv*, 2025.  
arXiv: 2510.25405  
- **thesis**: ソフトボディシミュレーションから得られる内部応力ペナルティをRL報酬に組み込むことで専用触覚センサなしに壊れやすい変形物体の穏やかな操作ポリシーをゼロショット転移で学習できる
- **core**: 平均応力＋上位10%応力中央値の二次変換によるストレスペナルティ報酬; カリキュラム学習（剛体代理→変形物体）＋RL with Prior Data (RLPD) フレームワーク
- **diff**: 専用触覚センサや精密物体モデルを必要とする先行手法に対しビジョンのみ入力とドメインランダム化で対応
- **limit**: シミュレーション-実世界のダイナミクス不一致; 物体多様性への拡張が今後の課題

**G3. Scheikl2023_RealtoSim**  
P. M. Scheikl et al. "Real-to-Sim Deformable Object Manipulation: Optimizing Physics Models with Residual Mappings for Robotic Surgery." *arXiv*, 2023.  
arXiv: 2309.11656  
- **thesis**: オンライン剛性パラメータ最適化と変形残差予測の同時実行によりsim-to-realギャップを閉じて自律ロボット外科手術の物理ベースシミュレーション追跡が可能
- **core**: Chamfer距離最小化による残差写像モジュール＋操作中の連続的剛性最適化; 体積物体向け幾何認識サブサーフェス変形
- **diff**: 残差のみまたはパラメータ最適化のみの先行手法に対し両方を組み合わせた初手法; 薄板モデルを超えた体積物体への拡張
- **limit**: 1ステップあたり0.9-2.6秒（リアルタイム不可）; 固定メッシュで組織の異方性を捉えられない

---

### Category H: Neural Dynamics / General

**H1. Lin2024_AdaptiGraph**  
Kaifeng Zhang, Baoyu Li, Kris Hauser, Yunzhu Li. "AdaptiGraph: Material-Adaptive Graph-Based Neural Dynamics for Robotic Manipulation." *RSS 2024*.  
arXiv: 2407.07889 | DOI: 10.15607/RSS.2024.XX.010  
- **thesis**: 明示的な物性変数に条件付けられた単一グラフニューラルダイナミクスモデルが多様な変形材料タイプに汎化し、オンラインのfew-shot逆最適化で未知物体に適応できる
- **core**: プロパティ条件付きグラフベース神経ダイナミクス (Graph-Based Neural Dynamics; GBND) モデル（材料タイプと物性値をノード特徴にエンコード）＋展開時にBO/CMA-ESによる逆最適化でオンライン物性推定
- **diff**: DPI-Net・GNS（材料別モデル・オンライン適応不可）に対し明示的物性推定による単一統一モデル
- **limit**: 4材料タイプのみで訓練; 材料あたり単一の物性

**H2. DiPac2024_DifferentiableParticles**  
D. Hsu et al. "Differentiable Particles for General-Purpose Deformable Object Manipulation." *ICRA 2024 workshop*.  
arXiv: 2405.01044  
- **thesis**: 統一粒子ベース微分MPMフレームワークがロープ・布・粒状体・液体など多様な変形タイプに汎用目的フレームワークとして機能し純粋モデルベース・純粋学習ベースを凌駕する
- **core**: 微分的軌跡木最適化: 勾配降下によるMPMパラメータ校正＋学習済み初期化ポリシー＋複数サンプル軌跡最適化で局所最適を回避
- **diff**: 物体タイプ別の先行手法に対し単一統一表現で異種変形を横断
- **limit**: オクルージョン下での粒子取得失敗; 不連続な最適化ランドスケープ

**H3. Huang2026_SoMA**  
M. Huang et al. "SoMA: A Real-to-Sim Neural Simulator for Robotic Soft-body Manipulation." *arXiv*, 2026.  
arXiv: 2602.02402  
- **thesis**: ロボット行動に条件付けられた3DGSニューラルシミュレータが事前定義された物理モデルや手動指定の材料パラメータなしに実映像から安定した長期ソフトボディ操作シミュレーションを実現できる
- **core**: ロボットキネマティクスに固定されたGaussianダイナミクス＋力駆動Gaussian伝播（階層的NN）＋マルチ解像度訓練＋オクルージョン認識画像損失
- **diff**: FEM/MPM/平滑化粒子流体力学 (Smoothed Particle Hydrodynamics; SPH)（パラメータ推定困難）・神経ダイナミクスモデル（ロボット行動条件付け不可）に対し学習変形ダイナミクス＋ロボット行動条件付けを初統合
- **limit**: 重度オクルージョン・訓練分布外接触で劣化; 4物体カテゴリのみで評価

---

### Category I: Benchmarks & Surveys

**I1. Huang2021_PlasticineLab** — (A7に記載)

**I2. Lin2021_SoftGym**  
Xingyu Lin, Yufei Wang, Jake Olkin, David Held. "SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation." *CoRL 2020*.  
arXiv: 2011.07215  
- **thesis**: RL向けの変形物体操作の標準化されたオープンソースシミュレーションスイートが欠如しており、現行RLアルゴリズムの失敗モードを明らかにするために必要
- **core**: FleXベースのOpenAI Gym互換変形物体操作環境（布・流体・ロープ）の標準ベンチマークスイート
- **diff**: MuJoCo/OpenAI Gym（剛体・直接状態観測）に対し高内在次元部分観測変形物体操作の初標準ベンチマーク
- **limit**: 高内在次元・部分観測性に対してRLアルゴリズムが苦戦; 物性推定やsim-to-realは未対応

**I3. Gu2023_SurveyDeformable**  
Feida Gu, Yanmin Zhou, Zhipeng Wang, et al. "A Survey on Robotic Manipulation of Deformable Objects: Recent Advances, Open Challenges and New Frontiers." *arXiv*, 2023.  
arXiv: 2312.10419  
- **thesis**: データ駆動手法と解析的物理モデルの統合が変形物体操作の核心課題である状態空間の無限次元性を克服する最も実行可能な経路
- **core**: 知覚・モデリング・操作戦略の3軸で150件超の研究を分類する分類法
- **diff**: Arriola-Rios 2020がモデルベース表現に焦点を当てるのに対しGNN・深層学習・LLMへの変形物体操作計画への応用を拡張
- **limit**: データ駆動手法は大規模データを必要とする; sim-to-realギャップが大きな障壁; LLM統合は更なる調査が必要

**I4. ArriaolaRios2020_ModelingReview**  
V. E. Arriola-Rios, P. Guler, F. Ficuciello, et al. "Modeling of Deformable Objects for Robotic Manipulation: A Tutorial and Review." *Frontiers in Robotics and AI*, 2020.  
DOI: 10.3389/frobt.2020.00082  
- **thesis**: 変形物体操作の効果的な実現には5つの統合された能力（形状表現・ダイナミクスモデリング・物理パラメータ学習・状態推定・操作計画）が必要でありいかなるロボットも全てを同時に持たない
- **core**: 形状表現・ダイナミクスモデル・パラメータ学習戦略（直接推定・誤差最小化・確率的手法）の統合チュートリアル兼レビュー
- **diff**: ドメイン固有の先行サーベイ（CG・CV・制御）に対しコンピュータグラフィクスの変形モデルとロボット操作計画を体系的に橋渡し
- **limit**: 体積固体変形物体に限定（DLO・気体・液体除外）; 新規材料のE・ν推定は未解決問題と明示

---

## Survey Methodology

### Search Log

| Phase | Source | Query / URL | Results | Relevance |
|-------|--------|-------------|---------|-----------|
| Angle A | WebSearch | "3D Gaussian Splatting" deformable "Young's modulus" robot | 10 | High |
| Angle A | WebSearch | "Gaussian Splatting" "material properties" deformable object estimation | 10 | High |
| Angle A | WebSearch | "PhysGaussian" OR "Gaussian material" deformable property estimation | 10 | High |
| Angle A | WebSearch | arxiv "Physically Embodied Gaussian Splatting" robot manipulation | 10 | High |
| Angle A | arXiv API | all:gaussian splatting deformable physical properties robot | Rate limited | — |
| Angle B | WebSearch | "Material Point Method" deformable "property estimation" robot manipulation | 10 | High |
| Angle B | WebSearch | "differentiable simulation" "Young's modulus" deformable robot | 10 | High |
| Angle B | WebSearch | "DiffTaichi" OR "Taichi" deformable "physical properties" robot manipulation | 10 | High |
| Angle B | WebSearch | "Differentiable Physics-based System Identification" Yang Ji Lai IJRR | 10 | Very High |
| Angle C | WebSearch | "spring-mass" OR "mass-spring" deformable "property estimation" robot | 10 | High |
| Angle C | WebSearch | "finite element" deformable "material identification" robot | 10 | High |
| Angle C | WebSearch | "graph neural network" deformable object manipulation physics | 10 | High |
| Angle C | WebSearch | survey "deformable object" manipulation robot "physical properties" | 10 | Very High |
| Angle D | WebSearch | deformable object manipulation "estimated material properties" robot real-world | 10 | High |
| Angle D | WebSearch | "sim-to-real" deformable "material estimation" robot manipulation task | 10 | High |
| Angle D | WebSearch | ICRA 2022 2023 2024 deformable "material properties" estimation robot | 10 | High |
| Angle D | WebSearch | CoRL 2022 2023 2024 deformable "physical properties" manipulation | 10 | High |
| Angle D | WebSearch | site:proceedings.mlr.press deformable "material" estimation robot | 10 | High |
| DOI Res. | WebSearch (×15) | Publisher DOI resolution for each paper | — | — |
| Verify | WebFetch (×15) | arXiv abstract page verification | 14/15 verified | — |

**Duplicates removed**: ~35件  
**Scope exclusions**: 外科組織のみ・粒状物体（砂・小麦粉）・切断・医療画像解析

### DOI Resolution Log

| Key | arXiv | Publisher DOI | Status |
|-----|-------|---------------|--------|
| Yang2024_DPSI | 2411.00554 | 10.1177/02783649251334661 | resolved |
| Cai2024_GIC | 2406.14927 | 10.5555/3737916.3740304 | resolved |
| Xie2023_PhysGaussian | 2311.12198 | 10.1109/CVPR52733.2024.00420 | resolved |
| Lin2024_AdaptiGraph | 2407.07889 | 10.15607/RSS.2024.XX.010 | resolved |
| Li2024_DLOFlexibility | 2410.23428 | 10.1109/ICRA57147.2024.10610419 | resolved |
| Patni2024_OnlineElasticity | 2401.08298 | 10.1007/s00170-024-13678-6 | resolved |
| Chen2024_PropriocepEstimation | 2410.03920 | 10.1109/ICRA55162.2025.11127955 | resolved |
| Yang2025_DDBot | 2510.17335 | 10.1109/TRO.2025.3636815 | resolved |
| Huang2023_DER | 2310.00911 | 10.1109/IROS60139.2025.11247160 | resolved |
| Liu2024_SoftMAC | 2312.03297 | 10.1109/IROS58592.2024.10801308 | resolved |
| Zheng2024_DiffCP | 2311.05141 | 10.1109/LRA.2024.3355731 | resolved |
| ArriaolaRios2020 | — | 10.3389/frobt.2020.00082 | resolved |
| Ying2024 | — | 10.1186/s40648-024-00283-1 | resolved |
| Yoon2025 | — | 10.1093/jcde/qwae069 | resolved |
| (27 papers) | various | — | arXiv only (ICLR/CoRL/PMLR = no publisher DOI) |

### Hallucination Check

| Paper | Status | Note |
|-------|--------|------|
| Yang2024_DPSI | ✓ verified | IJRR confirmed |
| Li2023_PACNeRF | ✓ verified | ICLR 2023 Spotlight confirmed |
| Lin2024_AdaptiGraph | ✓ verified | RSS 2024 confirmed |
| Xie2023_PhysGaussian | ✓ verified | CVPR 2024 confirmed |
| Liu2024_Physics3D | ⚠ venue corrected | **Not NeurIPS 2024** — ICLR 2025 submission withdrawn; treated as arXiv preprint |
| Cai2024_GIC | ✓ verified | NeurIPS 2024 Oral confirmed |
| AbouChakra2024_EmbodiedGS | ✓ verified | CoRL 2024 / PMLR confirmed |
| Cheng2024_DEFORM | ✓ verified | CoRL 2024 confirmed (not ICLR 2025) |
| ArriaolaRios2020 | ✓ verified | Frontiers DOI confirmed |
| (11 spot-checked) | ✓ all verified | — |

### Limit Field Coverage

| Category | Papers with explicit limit | Papers with "not explicitly stated" |
|----------|---------------------------|-------------------------------------|
| Diff-Physics/MPM | 8/8 (100%) | 0 |
| 3DGS-Physics | 6/6 (100%) | 0 |
| Spring-mass/Hybrid | 3/3 (100%) | 0 |
| Cloth/ThinShell | 4/4 (100%) | 0 |
| DLO | 4/4 (100%) | 0 |
| Tactile/Sensing | 4/5 (80%) | 1 (Chen2024_PropriocepEstimation) |
| Sim-to-Real/Task | 3/3 (100%) | 0 |
| Neural Dynamics | 3/3 (100%) | 0 |
| Benchmarks | 4/4 (100%) | 0 |
| **Total** | **39/41 (95%)** | **2** |

---

## 略語一覧

| 略語 | 完全名 | 初出カテゴリ |
|------|--------|-------------|
| AD | Automatic Differentiation（自動微分） | Category A: DiffTaichi |
| AEP | Anisotropic Elasto-Plastic（異方性弾塑性） | Category D: DiffCP |
| BO | Bayesian Optimization（ベイズ最適化） | Foundation Building Block 3 |
| CMA-ES | Covariance Matrix Adaptation Evolution Strategy（共分散行列適応進化戦略） | Foundation Building Block 3 |
| DDPG | Deep Deterministic Policy Gradient（深層決定論的方策勾配法） | Foundation Building Block 4 |
| DER | Discrete Elastic Rods（離散弾性ロッド） | Foundation Building Block 1 |
| DLO | Deformable Linear Object（変形線形物体） | Foundation Building Block 1 |
| EMD | Earth Mover's Distance | Foundation Building Block 1 |
| GBND | Graph-Based Neural Dynamics（グラフベース神経ダイナミクス） | Category H: AdaptiGraph |
| GNN | Graph Neural Network（グラフニューラルネットワーク） | Category A: DDBot |
| IPC | Incremental Potential Contact（増分ポテンシャル接触） | Seed 1 |
| LBS | Linear Blend Skinning（線形ブレンドスキニング） | Category C: Real2SimSoft |
| LLM | Large Language Model（大規模言語モデル） | Category F: YoungModulus |
| MLP | Multi-Layer Perceptron（多層パーセプトロン） | Category F: DiffTactile |
| MLS-MPM | Moving Least Squares Material Point Method（移動最小二乗MPM） | Category A: DPSI |
| MPC | Model Predictive Control（モデル予測制御） | Category E: Ying2024 |
| NeRF | Neural Radiance Field（ニューラル輝度場） | Foundation Building Block 5 |
| NN | Neural Network（ニューラルネット） | Category B: OmniPhysGS |
| PBD | Position-Based Dynamics（位置ベースダイナミクス） | Category B: EmbodiedGS |
| PPO | Proximal Policy Optimization（近位方策最適化） | Category E: DER |
| RGB-D | RGB-Depth（RGB-深度） | Thesis |
| RL | Reinforcement Learning（強化学習） | Category A: DDBot |
| RLPD | RL with Prior Data | Category G: StressGuidedRL |
| SAC | Soft Actor-Critic（ソフト・アクター・クリティック） | Category E: DLOFlexibility |
| SAM | Segment Anything Model（セグメント・エニシング・モデル） | Category B: PhysGS |
| SDS | Score Distillation Sampling（スコア蒸留サンプリング） | Category B: Physics3D |
| SPH | Smoothed Particle Hydrodynamics（平滑化粒子流体力学） | Category H: SoMA |
| StVK | Saint Venant-Kirchhoff（サン・ブナン・キルヒホッフ弾性） | Category A: DDBot |
| SVD | Singular Value Decomposition（特異値分解） | Category A: PlasticineLab |
| VLM | Vision-Language Model（視覚言語モデル） | Category B: PhysGS |
| WS2 | What You See is What You Simulate | Foundation Building Block 2 |
