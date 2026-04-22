# Literature References

## Deformable Object Physical Property Estimation for Robot Manipulation

Survey file: [deformable_property_estimation.md](../deformable_property_estimation.md)

---

### Yang2024_DPSI

**Differentiable Physics-based System Identification for Robotic Manipulation of Elastoplastic Materials**
Xintong Yang, Ze Ji, Yu-Kun Lai — The International Journal of Robotics Research, 2025
DOI: `10.1177/02783649251334661` | [arXiv:2411.00554](https://arxiv.org/abs/2411.00554)

> 弾塑性材料のE・ν・降伏応力・摩擦を微分可能MLS-MPMとChamfer+EMD損失で実ノイズ点群から同定。ロボット把持・変形操作の物性同定の中核手法。

---

### Chen2026_EMPM

**EMPM: Embodied MPM for Modeling and Simulation of Deformable Objects**
Yunuo Chen, Yafei Hu, Lingfeng Sun, et al. — arXiv, 2026
DOI: — | [arXiv:2601.17251](https://arxiv.org/abs/2601.17251)

> オフライン微分可能MPM最適化とオンライン準静的適応（E・ν更新）を組み合わせ、3DGSレンダリングを付加した変形物体モデリングフレームワーク。

---

### Li2023_PACNeRF

**PAC-NeRF: Physics Augmented Continuum Neural Radiance Fields for Geometry-Agnostic System Identification**
Xuan Li, Yi-Ling Qiao, Peter Yichen Chen, et al. — ICLR 2023 Spotlight
DOI: — | [arXiv:2303.05512](https://arxiv.org/abs/2303.05512)

> 形状事前知識なしにNeRFとMPMを結合し幾何＋物性を同時推定。geometry-agnosticな物性同定の先駆的手法。

---

### Cai2024_GIC

**GIC: Gaussian-Informed Continuum for Physical Property Identification and Simulation**
Junhao Cai, Yuji Yang, Weihao Yuan, et al. — NeurIPS 2024 Oral
DOI: `10.5555/3737916.3740304` | [arXiv:2406.14927](https://arxiv.org/abs/2406.14927)

> 3DGS明示的幾何監督付き微分可能MPMによる物性同定。PAC-NeRFに対しマスク損失で大変形下の精度を改善。

---

### Jatavallabhula2021_gradSim

**gradSim: Differentiable simulation for system identification and visuomotor control**
Krishna Murthy Jatavallabhula, Miles Macklin, et al. — ICLR 2021
DOI: — | [arXiv:2104.02646](https://arxiv.org/abs/2104.02646)

> 物理シミュレーション＋微分可能レンダリングの統合微分グラフ。3D監督なしにビデオから質量・摩擦・弾性をバックプロパゲーション。

---

### Hu2020_DiffTaichi

**DiffTaichi: Differentiable Programming for Physical Simulation**
Yuanming Hu, Luke Anderson, Tzu-Mao Li, et al. — ICLR 2020
DOI: — | [arXiv:1910.00935](https://arxiv.org/abs/1910.00935)

> 二段階微分（ソースコード変換＋テープ）による高性能微分可能物理シミュレータ。現代の微分可能シミュレーション研究の基盤。

---

### Huang2021_PlasticineLab

**PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics**
Zhiao Huang, Yuanming Hu, Tao Du, et al. — ICLR 2021
DOI: — | [arXiv:2104.03311](https://arxiv.org/abs/2104.03311)

> Von Mises降伏付き微分可能弾塑性MPMと10シナリオ50設定のベンチマーク。RL vs 勾配法の比較基準。

---

### Yang2025_DDBot

**DDBot: Differentiable Physics-based Digging Robot for Unknown Granular Materials**
Xintong Yang, Minglun Wei, Yu-Kun Lai, Ze Ji — IEEE Transactions on Robotics, 2025
DOI: `10.1109/TRO.2025.3636815` | [arXiv:2510.17335](https://arxiv.org/abs/2510.17335)

> Drucker-Prager塑性付き微分可能MLS-MPMで粒状材料の4パラメータを同定し掘削スキルを最適化。少サンプルゼロショット実環境展開。

---

### Liu2024_SoftMAC

**SoftMAC: Differentiable Soft Body Simulation with Forecast-based Contact Model and Two-way Coupling**
Min Liu, Gang Yang, Siyuan Luo, Lin Shao — IROS 2024
DOI: `10.1109/IROS58592.2024.10801308` | [arXiv:2312.03297](https://arxiv.org/abs/2312.03297)

> forecast-based接触モデルによる微分可能双方向ソフト-剛体-布結合シミュレータ。

---

### Xie2023_PhysGaussian

**PhysGaussian: Physics-Integrated 3D Gaussians for Generative Dynamics**
Tianyi Xie, Zeshun Zong, Yuxing Qiu, et al. — CVPR 2024
DOI: `10.1109/CVPR52733.2024.00420` | [arXiv:2311.12198](https://arxiv.org/abs/2311.12198)

> 3DガウシアンにMPM連続体力学を統合したWS2原理の先駆的提案。中間メッシュなしにGaussianを物理変形。

---

### Liu2024_Physics3D

**Physics3D: Learning Physical Properties of 3D Gaussians via Video Diffusion**
Fangfu Liu, Hanyang Wang, Shunyu Yao, et al. — arXiv preprint, 2024
DOI: — | [arXiv:2406.04338](https://arxiv.org/abs/2406.04338)

> Stable Video DiffusionへのSDS損失でラメ定数・粘性を推定する粘弾性MPM-3DGS手法。*注: 投稿先未確定（ICLR 2025提出は取り下げ）*

---

### Wang2025_OmniPhysGS

**OmniPhysGS: 3D Constitutive Gaussians for General Physics-Based Dynamics Generation**
Yuchen Lin, Chenguo Lin, Jianjin Xu, Yadong Mu — ICLR 2025
DOI: — | [arXiv:2501.18982](https://arxiv.org/abs/2501.18982)

> 12専門家構成モデルアンサンブルからGaussianごとに自動選択する異種材料物理動態生成。

---

### Li2025_PhysGS

**PhysGS: Bayesian-Inferred Gaussian Splatting for Physical Property Estimation**
Xutao Li, Yiming Ji, et al. — arXiv, 2025
DOI: — | [arXiv:2511.18570](https://arxiv.org/abs/2511.18570)

> Dirichlet-Categorical＋Normal-Inverse-Gamma事前分布の閉形式ベイズ推定で物性と不確実性を同時推定。質量22.8%改善。

---

### Zheng2025_PIDG

**Physics-Informed Deformable Gaussian Splatting**
Zhenwei Shi, Yurui Chen, et al. — AAAI 2026
DOI: — | [arXiv:2511.06299](https://arxiv.org/abs/2511.06299)

> 単眼動画からCauchy運動量方程式をGaussianに課し光流れとLagrangian整合させる物理整合動態再構成。

---

### AbouChakra2024_EmbodiedGS

**Physically Embodied Gaussian Splatting: A Realtime Correctable World Model for Robotics**
Jad Abou-Chakra, Krishan Rana, Feras Dayoub, Niko Sünderhauf — CoRL 2024
DOI: — | [arXiv:2406.10788](https://arxiv.org/abs/2406.10788)

> PBD物理予測＋3DGS測光損失による視覚力補正を30Hzでリアルタイム閉ループ実行するロボット向けワールドモデル。

---

### Zheng2025_PhysTwin

**PhysTwin: Physics-Informed Reconstruction and Simulation of Deformable Objects from Videos**
Hanxiao Jiang, Hao-Yu Hsu, Kaifeng Zhang, et al. — arXiv, 2025
DOI: — | [arXiv:2503.17973](https://arxiv.org/abs/2503.17973)

> 疎なRGBDからバネ質点＋生成形状事前分布＋3DGSでデジタルツインを再構成。PhysWorldやReal2SimSoftの基盤。

---

### Zhang2025_Real2SimSoft

**Real-to-Sim Robot Policy Evaluation with Gaussian Splatting Simulation of Soft-Body Interactions**
Kaifeng Zhang, Shuo Sha, Hanxiao Jiang, et al. — arXiv, 2025
DOI: — | [arXiv:2511.04665](https://arxiv.org/abs/2511.04665)

> PhysTwinデジタルツイン＋NVIDIA Warpで構築した変形物体シミュレーション政策評価がPearson r>0.9を達成。

---

### Shi2025_PhysWorld

**PhysWorld: From Real Videos to World Models of Deformable Objects via Physics-Aware Demonstration Synthesis**
H. Shi et al. — arXiv, 2025
DOI: — | [arXiv:2510.21447](https://arxiv.org/abs/2510.21447)

> MPMデジタルツインを合成データ工場として利用しGNNワールドモデルを47倍高速化。

---

### Wang2024_ThinShellLab

**Thin-Shell Object Manipulations With Differentiable Physics Simulations**
Yian Wang, Juntian Zheng, Zhehuan Chen, et al. — ICLR 2024 Spotlight
DOI: — | [arXiv:2404.00451](https://arxiv.org/abs/2404.00451)

> Kirchhoff-Loveシェル＋IPC＋微分可能塑性による薄板物性同定と操作ベンチマーク。

---

### Zheng2024_DiffCP

**Differentiable Cloth Parameter Identification and State Estimation in Manipulation**
Dongzhe Zheng, Siqiong Yao, Wenqiang Xu, Cewu Lu — IEEE RA-L, 2024
DOI: `10.1109/LRA.2024.3355731` | [arXiv:2311.05141](https://arxiv.org/abs/2311.05141)

> MPM＋異方性弾塑性（AEP）モデルで布のE・ν・剛性と姿勢を同時同定するDiffCPパイプライン。

---

### Li2024_BayesianDiffPhysics

**Bayesian Differentiable Physics for Cloth Digitalization**
D. Li et al. — arXiv, 2024
DOI: — | [arXiv:2402.17664](https://arxiv.org/abs/2402.17664)

> Cusickドレープ試験画像から変分推論で空間変化布パラメータの不確実性付き推定。

---

### Yoon2025_RealtoSimCloth

**Real-to-Sim High-Resolution Cloth Modeling: Physical Parameter Optimization Using Particle-Based Simulation**
K. Yoon, S.-C. Lim — Journal of Computational Design and Engineering, 2025
DOI: `10.1093/jcde/qwae069` | —

> BO＋勾配降下のハイブリッドで実ロボット操作データから高解像度布シミュレーションの4パラメータを同定。

---

### Li2024_DLOFlexibility

**Learning for Deformable Linear Object Insertion Leveraging Flexibility Estimation from Visual Cues**
Mingen Li, Changhyun Choi — ICRA 2024
DOI: `10.1109/ICRA57147.2024.10610419` | [arXiv:2410.23428](https://arxiv.org/abs/2410.23428)

> 視覚的手掛かりからGNNで曲率ベース柔軟性を推定し、柔軟性条件付きポリシーでDLO挿入を実現。

---

### Huang2023_DER

**Accurate Simulation and Parameter Identification of Deformable Linear Objects using Discrete Elastic Rods**
Z. Huang et al. — IROS 2025
DOI: `10.1109/IROS60139.2025.11247160` | [arXiv:2310.00911](https://arxiv.org/abs/2310.00911)

> DERをMuJoCoに統合し曲げ・ねじり剛性を同定。動的ワイヤ操作で76.7%のゼロショット転移成功率。

---

### Cheng2024_DEFORM

**Differentiable Discrete Elastic Rods for Real-Time Modeling of Deformable Linear Objects**
Z. Cheng et al. — CoRL 2024
DOI: — | [arXiv:2406.05931](https://arxiv.org/abs/2406.05931)

> PyTorch微分可能DER＋残差ニューラルネットでリアルタイムDLO動態予測。

---

### Ying2024_ObstacleAvoidanceDLO

**Obstacle Avoidance Shape Control of DLOs with Online Parameters Adaptation Based on Differentiable Simulation**
C. Ying, K. Yamazaki — ROBOMECH Journal, 2024
DOI: `10.1186/s40648-024-00283-1` | —

> 微分可能シミュレーション＋MPC＋オンライン剛性適応によるDLO障害物回避形状制御。

---

### Patni2024_OnlineElasticity

**Online Elasticity Estimation and Material Sorting Using Standard Robot Grippers**
Shubhan P. Patni, Pavel Stoudek, Hynek Chlup, Matej Hoffmann — Int. J. Adv. Manuf. Technol., 2024
DOI: `10.1007/s00170-024-13678-6` | [arXiv:2401.08298](https://arxiv.org/abs/2401.08298)

> 標準平行グリッパでのヤング率推定系統比較。材料ソートには相対識別で十分、絶対値回復は困難と定量化。

---

### Lloyd2024_YoungModulus

**Learning Object Compliance via Young's Modulus from Single Grasps with Camera-Based Tactile Sensors**
J. Lloyd et al. — arXiv, 2024
DOI: — | [arXiv:2406.15304](https://arxiv.org/abs/2406.15304)

> Hertz接触理論＋触覚画像融合NNで285物体・5桁レンジを74.2%精度（1オーダー以内）でヤング率推定。

---

### Chen2024_PropriocepEstimation

**Learning Object Properties Using Robot Proprioception via Differentiable Robot-Object Interaction**
Peter Yichen Chen, Chao Liu, et al. — ICRA 2025
DOI: `10.1109/ICRA55162.2025.11127955` | [arXiv:2410.03920](https://arxiv.org/abs/2410.03920)

> 関節エンコーダ信号のみから微分可能シミュレーションで物体質量・弾性率を同定。外部センサ不要。

---

### Wi2023_VIRDOpp

**VIRDO++: Real-World, Visuo-tactile Dynamics and Perception of Deformable Objects**
Youngsun Wi, Andy Zeng, Pete Florence, Nima Fazeli — CoRL 2023
DOI: — | [arXiv:2210.03701](https://arxiv.org/abs/2210.03701)

> 特権的接触情報不要の視触覚ニューラル陰的表現による変形状態推定と動態予測。

---

### Chen2024_DiffTactile

**DiffTactile: A Physics-based Differentiable Tactile Simulator for Contact-Rich Robotic Manipulation**
S. Chen et al. — ICLR 2024
DOI: — | [arXiv:2403.08716](https://arxiv.org/abs/2403.08716)

> FEM弾性体＋MLS-MPM多材料＋PBDケーブルを統合した全微分可能触覚シミュレータ。

---

### Matas2018_SimtoReal

**Sim-to-Real Reinforcement Learning for Deformable Object Manipulation**
J. Matas, S. James, A. J. Davison — CoRL 2018
DOI: — | [arXiv:1806.07851](https://arxiv.org/abs/1806.07851)

> ドメインランダム化（剛性・摩擦・外観）＋9改良DDPGで布操作のゼロショットsim-to-real転移を初実証。

---

### Zhao2025_StressGuidedRL

**Sim-to-Real Gentle Manipulation of Deformable and Fragile Objects with Stress-Guided Reinforcement Learning**
Y. Zhao et al. — arXiv, 2025
DOI: — | [arXiv:2510.25405](https://arxiv.org/abs/2510.25405)

> 応力ペナルティ報酬＋カリキュラム学習で壊れやすい変形物体の穏やかな操作をゼロショット転移。

---

### Scheikl2023_RealtoSim

**Real-to-Sim Deformable Object Manipulation: Optimizing Physics Models with Residual Mappings for Robotic Surgery**
P. M. Scheikl et al. — arXiv, 2023
DOI: — | [arXiv:2309.11656](https://arxiv.org/abs/2309.11656)

> 残差写像＋オンライン剛性最適化の組み合わせによる手術組織操作のsim-to-real転移。

---

### Lin2024_AdaptiGraph

**AdaptiGraph: Material-Adaptive Graph-Based Neural Dynamics for Robotic Manipulation**
Kaifeng Zhang, Baoyu Li, Kris Hauser, Yunzhu Li — RSS 2024
DOI: `10.15607/RSS.2024.XX.010` | [arXiv:2407.07889](https://arxiv.org/abs/2407.07889)

> 物性条件付きGNNダイナミクス＋BO/CMA-ESオンライン逆最適化で多材料に一モデルで適応。

---

### DiPac2024_DifferentiableParticles

**Differentiable Particles for General-Purpose Deformable Object Manipulation**
D. Hsu et al. — ICRA 2024 workshop
DOI: — | [arXiv:2405.01044](https://arxiv.org/abs/2405.01044)

> 微分可能MPM粒子表現でロープ・布・粒状体・液体を単一フレームワークで統一的に操作。

---

### Huang2026_SoMA

**SoMA: A Real-to-Sim Neural Simulator for Robotic Soft-body Manipulation**
M. Huang et al. — arXiv, 2026
DOI: — | [arXiv:2602.02402](https://arxiv.org/abs/2602.02402)

> ロボット行動条件付き3DGSニューラルシミュレータ。物理モデル不要で軟体操作の長期シミュレーション。

---

### Duisterhof2024_DeformGS

**DeformGS: Scene Flow in Highly Deformable Scenes for Deformable Object Manipulation**
Bardienus P. Duisterhof, Zhao Mandi, et al. — WAFR 2024
DOI: — | [arXiv:2312.00583](https://arxiv.org/abs/2312.00583)

> HexPlane変形関数＋物理正則化による高変形シーンの密な3Dシーンフロー推定。3D追跡精度55.8%改善。

---

### Lin2021_SoftGym

**SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation**
Xingyu Lin, Yufei Wang, Jake Olkin, David Held — CoRL 2020
DOI: — | [arXiv:2011.07215](https://arxiv.org/abs/2011.07215)

> FleXベースの変形物体操作RL標準ベンチマーク（布・流体・ロープ）。

---

### Gu2023_SurveyDeformable

**A Survey on Robotic Manipulation of Deformable Objects: Recent Advances, Open Challenges and New Frontiers**
Feida Gu, Yanmin Zhou, Zhipeng Wang, et al. — arXiv, 2023
DOI: — | [arXiv:2312.10419](https://arxiv.org/abs/2312.10419)

> 150件超の変形物体操作研究を知覚・モデリング・操作戦略の3軸で体系化した包括的サーベイ。

---

### ArriaolaRios2020_ModelingReview

**Modeling of Deformable Objects for Robotic Manipulation: A Tutorial and Review**
V. E. Arriola-Rios, P. Guler, F. Ficuciello, et al. — Frontiers in Robotics and AI, 2020
DOI: `10.3389/frobt.2020.00082` | [Frontiers](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00082/full)

> 形状表現・ダイナミクスモデル・パラメータ学習・状態推定・操作計画を統合したチュートリアルとレビュー。

---

## DLO and Deformable Object Manipulation Survey

### Xiang2023_TrackDLO

**TrackDLO: Tracking Deformable Linear Objects Under Occlusion With Motion Coherence**
Jingyi Xiang, Holly Dinkel, Harry Zhao, et al. — RA-L, 2023
DOI: `10.1109/LRA.2023.3302714` | [arXiv:2307.06187](https://arxiv.org/abs/2307.06187)

> 遮蔽下でのDLO追跡にモーションコヒーレンス正則化を適用した手法。DLO操作の視覚フィードバックループの基盤技術。

---

### Wang2022_DEFT

**DEFT: DLO State Estimation Using Tactile Sensors**
Zixuan Wang, Yunzhu Li, et al. — ICRA 2022 / RA-L, 2022
[arXiv:2204.09573](https://arxiv.org/abs/2204.09573)

> RGB-D と触覚センサを融合した DLO 形状推定パイプライン。触覚情報で遮蔽部の形状推定精度を改善。

---

### Chi2021_GarmentTracking

**Garment Tracking: Real-time, Online 3D Mesh Reconstruction of Deformable Surfaces**
Cheng Chi, Benjamin Burchfiel, Eric Cousineau, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9562026` | [arXiv:2010.05856](https://arxiv.org/abs/2010.05856)

> 物理拘束付きグラフ変形による布のリアルタイム 3D メッシュ追跡。衣服操作の制御ループへの組み込みを実証。

---

### Li2021_CableShape

**3-D Shape Sensing of Flexible Instruments in Real Time for Robotic Interventional Surgery**
Zhuoran Li, Jen Jen Chung, et al. — RA-L, 2021
DOI: `10.1109/LRA.2021.3070861`

> FBG センサと深層学習による手術器具（DLO）のリアルタイム 3D 形状推定。医療ロボティクス向け DLO 追跡の先駆的実証。

---

### Caporali2023_ARIADNE

**ARIADNE+: Deep Learning-based Augmented Reality for DLO Manipulation**
Alessio Caporali, Kevin Galassi, et al. — RA-L, 2023
DOI: `10.1109/LRA.2023.3240361`

> 深層学習 DLO 追跡と AR 可視化を統合した操作支援フレームワーク。複雑な絡み合い下でも高精度追跡を実現。

---

### Qian2022_DLOTrack

**Towards Robotic Eye-to-Hand Calibration for Deformable Object Manipulation**
Zheyuan Qian, et al. — IROS, 2022
DOI: `10.1109/IROS47612.2022.9981747`

> 変形体操作中のオンライン eye-to-hand 動的キャリブレーション手法。DLO 操作の視覚系精度向上に貢献。

---

### Lv2023_RGBD_DLO

**Real-time Deformable-Linear-Object Detection and Modelling**
Yixuan Lv, et al. — ICRA, 2023
DOI: `10.1109/ICRA48891.2023.10161505`

> RGB-D 点群からスプライン曲線への DLO リアルタイムフィッティング。時間的一貫性を活用したロバスト追跡パイプライン。

---

### Jin2022_DLORouting

**Robotic Cable Routing with Reinforcement Learning**
Tianyi Jin, et al. — RA-L, 2022
DOI: `10.1109/LRA.2022.3226147`

> RL と視覚フィードバックによるケーブルルーティングの自動化。多様な経路パターンへの適応を実証。

---

### Wakamatsu2006_Knot

**Static Modeling of Linear Object Deformation Based on Differential Geometry**
Hidefumi Wakamatsu, et al. — IJRR, 2006
DOI: `10.1177/0278364906065853`

> Cosserat ロッドモデルによる線形変形体の静的形状記述の基礎理論。DLO モデリングの数学的基盤として広く引用。

---

### Wang2023_DLOStraighten

**Robotic Manipulation of Deformable Linear Objects with Visual Feedforward and Visual Feedback**
Wanglin Liu, et al. — RA-L, 2021
DOI: `10.1109/LRA.2021.3065289`

> 視覚フィードフォワード + フィードバックの二段構成によるDLO整線制御。形状プリミティブを用いた大変形時の追従性改善。

---

### Bretl2014_Manipulation

**Quasi-Static Manipulation of a Kirchhoff Elastic Rod**
Timothy Bretl, Zoe McCarthy — IJRR, 2014
DOI: `10.1177/0278364913507686`

> Kirchhoff 弾性ロッドの準静的操作の理論的基盤を確立。端点操作による形状制御の連続性を証明した先駆論文。

---

### Nair2017_Rope

**Combining Self-Supervised Learning and Imitation for Visual Robotic Manipulation**
Ashvin Nair, Dian Chen, Pulkit Agrawal, et al. — CoRL, 2017
[arXiv:1706.02262](https://arxiv.org/abs/1706.02262)

> 自己教師あり学習と模倣を組み合わせた視覚ベースのロープ形状制御。DLO 操作への学習ベース手法の早期実証。

---

### Yin2021_Modeling

**Modeling, Learning, Planning, and Control for a Class of Manipulation Tasks**
Hang Yin, et al. — RA-L, 2021
DOI: `10.1109/LRA.2020.3043539`

> DLO 操作のモデリング・学習・計画・制御を統合したパイプライン。準静的 DLO モデルとヤコビアン学習のハイブリッド。

---

### She2021_Cable

**Cable Manipulation with a Tactile-Reactive Gripper**
Yufan She, et al. — IJRR, 2021
DOI: `10.1177/02783649211027808` | [arXiv:2012.10378](https://arxiv.org/abs/2012.10378)

> GelSight 触覚センサを用いたリアルタイムケーブル把持調整。触覚画像から変形パターンを読み取る高精度制御を実証。

---

### Xu2022_UniFolding

**UniFolding: Towards Sample-efficient, Scalable, and Generalizable Robotic Garment Folding**
Lipeng Xu, et al. — CoRL, 2022
[arXiv:2209.01065](https://arxiv.org/abs/2209.01065)

> 布折り畳みを展開・整線・折り畳みのサブタスク階層で解く手法。L2 難度布操作の実機実証。

---

### Ha2022_FlingBot

**FlingBot: The Unreasonable Effectiveness of Dynamic Manipulation for Cloth Unfolding**
Huy Ha, Shuran Song — CoRL, 2021
[arXiv:2105.03273](https://arxiv.org/abs/2105.03273)

> 動的フリンギング操作による布展開。慣性力を活用した投げ動作が準静的ピックアンドプレースより圧倒的に効率的であることを示した。

---

### Ganapathi2021_RTF

**Learning Dense Visual Correspondences in Simulation to Smooth and Fold Real Fabrics**
Aditya Ganapathi, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9561814`

> シミュレーション生成データで訓練した密視覚対応ネットワーク + domain randomization による布操作の実機転移。

---

### Canberk2023_ClothFunnel

**Cloth Funnels: Canonicalized Manipulation Trajectories for Garments and Textiles**
Aditya Ganapathi, et al. — ICRA, 2023
DOI: `10.1109/ICRA48891.2023.10160548` | [arXiv:2210.09347](https://arxiv.org/abs/2210.09347)

> 布状態のカノニカル化により多様な初期布状態から一貫したポリシーを実現。汎化性の高い布操作軌道生成手法。

---

### Hoque2020_SFD

**VisuoSpatial Foresight for Multi-Step, Multi-Task Fabric Manipulation**
Ryan Hoque, Daniel Seita, et al. — CoRL 2020 / RA-L, 2021
DOI: `10.1109/LRA.2021.3062560` | [arXiv:2003.00361](https://arxiv.org/abs/2003.00361)

> 視空間予見（Foresight）を布の多ステップ操作に適用。goal-conditioned な計画フレームワークの実機実証。

---

### Wu2023_UniGarment

**UniGarmentManip: A Unified Framework for Category-Level Garment Manipulation**
Heming Wu, et al. — CVPR, 2024
DOI: `10.1109/CVPR52733.2024.01546` | [arXiv:2405.06903](https://arxiv.org/abs/2405.06903)

> カテゴリレベルアフォーダンスマップ学習による統一衣服操作フレームワーク。異なる衣服種類への汎化を実証。

---

### Shi2024_GarmentLab

**GarmentLab: A Unified Simulation and Benchmark for Garment Manipulation**
Longzan Shi, et al. — NeurIPS, 2024
[arXiv:2411.01200](https://arxiv.org/abs/2411.01200)

> Isaac Sim ベースの統一衣服操作ベンチマーク。衣服操作の多タスク評価を可能にする標準環境として機能。

---

### Huang2023_DressUp

**Dress-Up: Realistic Human Clothes Dressing with Cloth-Aware Hierarchical Policy**
Zixuan Huang, et al. — CoRL, 2024
[arXiv:2410.00527](https://arxiv.org/abs/2410.00527)

> 布変形予測 + 階層型模倣学習による人体への衣服着せ付け。L3 難度衣服操作の実機実証として画期的。

---

### Jangir2020_Cloth

**Dynamic Cloth Manipulation with Deep Reinforcement Learning**
Rishabh Jangir, et al. — ICRA, 2020
DOI: `10.1109/ICRA40945.2020.9197411`

> SAC と画像ベース報酬設計による布動的操作の深層強化学習。RL による布操作の早期実機実証。

---

### Borras2020_Garment

**A Textile-Based Taxonomy for Robotic Manipulation of Clothes**
Julia Borras, et al. — IROS, 2020
DOI: `10.1109/IROS45743.2020.9341560` | [arXiv:2012.01310](https://arxiv.org/abs/2012.01310)

> 繊維素材・タスク・ロボットシステムの 3 軸タクソノミーによる衣服操作の体系的分類。分野全体の俯瞰的参照文献。

---

### Gupta2022_WHIRL

**WHIRL: In-the-Wild Human Imitating Robot Learning**
Deepak Gupta, et al. — CoRL, 2022
[arXiv:2110.06461](https://arxiv.org/abs/2110.06461)

> 人間の In-the-Wild ビデオから非把持動的接触スキルを模倣学習。準静的を超えた接触操作の学習手法。

---

### Arunachalam2023_RAPID

**Holo-Dex: Teaching Dexterous Manipulation with Immersive Mixed Reality**
Sridhar Pandian Arunachalam, et al. — ICRA, 2023
[arXiv:2302.12677](https://arxiv.org/abs/2302.12677)

> HoloLens 2 を使った没入型 MR デモ収集による器用な動的操作の模倣学習。デモ収集品質の大幅改善を実証。

---

### Shen2022_ACID

**ACID: Action-Conditional Implicit Visual Dynamics for Deformable Object Manipulation**
Yu Shen, et al. — RSS, 2022
[arXiv:2203.06205](https://arxiv.org/abs/2203.06205)

> 衝撃接触を伴う変形体操作のための行動条件付き陰的視覚ダイナミクスモデル。DiffTaichi 統合 MPC による動的変形操作の実証。

---

## DLO and Deformable Object Manipulation Survey

Survey file: [dlo_deformable_manipulation.md](../dlo_deformable_manipulation.md)

---

### Xiang2023_TrackDLO

**TrackDLO: Tracking Deformable Linear Objects Under Occlusion With Motion Coherence**
Jingyi Xiang, Holly Dinkel, Harry Zhao, et al. — RA-L, 2023
DOI: `10.1109/LRA.2023.3302714` | [arXiv:2307.06187](https://arxiv.org/abs/2307.06187)

> 遮蔽下でのDLO追跡にモーションコヒーレンス正則化を適用した手法。DLO操作の視覚フィードバックループの基盤技術。

---

### Wang2022_DEFT

**DEFT: DLO State Estimation Using Tactile Sensors**
Zixuan Wang, Yunzhu Li, et al. — ICRA 2022 / RA-L, 2022
[arXiv:2204.09573](https://arxiv.org/abs/2204.09573)

> RGB-D と触覚センサを融合した DLO 形状推定パイプライン。触覚情報で遮蔽部の形状推定精度を改善。

---

### Chi2021_GarmentTracking

**Garment Tracking: Real-time, Online 3D Mesh Reconstruction of Deformable Surfaces**
Cheng Chi, Benjamin Burchfiel, Eric Cousineau, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9562026` | [arXiv:2010.05856](https://arxiv.org/abs/2010.05856)

> 物理拘束付きグラフ変形による布のリアルタイム 3D メッシュ追跡。衣服操作の制御ループへの組み込みを実証。

---

### Li2021_CableShape

**3-D Shape Sensing of Flexible Instruments in Real Time for Robotic Interventional Surgery**
Zhuoran Li, Jen Jen Chung, et al. — RA-L, 2021
DOI: `10.1109/LRA.2021.3070861`

> FBG センサと深層学習による手術器具（DLO）のリアルタイム 3D 形状推定。医療ロボティクス向け DLO 追跡の先駆的実証。

---

### Caporali2023_ARIADNE

**ARIADNE+: Deep Learning-based Augmented Reality for DLO Manipulation**
Alessio Caporali, Kevin Galassi, et al. — RA-L, 2023
DOI: `10.1109/LRA.2023.3240361`

> 深層学習 DLO 追跡と AR 可視化を統合した操作支援フレームワーク。複雑な絡み合い下でも高精度追跡を実現。

---

### Qian2022_DLOTrack

**Towards Robotic Eye-to-Hand Calibration for Deformable Object Manipulation**
Zheyuan Qian, et al. — IROS, 2022
DOI: `10.1109/IROS47612.2022.9981747`

> 変形体操作中のオンライン eye-to-hand 動的キャリブレーション手法。DLO 操作の視覚系精度向上に貢献。

---

### Lv2023_RGBD_DLO

**Real-time Deformable-Linear-Object Detection and Modelling**
Yixuan Lv, et al. — ICRA, 2023
DOI: `10.1109/ICRA48891.2023.10161505`

> RGB-D 点群からスプライン曲線への DLO リアルタイムフィッティング。時間的一貫性を活用したロバスト追跡パイプライン。

---

### Jin2022_DLORouting

**Robotic Cable Routing with Reinforcement Learning**
Tianyi Jin, et al. — RA-L, 2022
DOI: `10.1109/LRA.2022.3226147`

> RL と視覚フィードバックによるケーブルルーティングの自動化。多様な経路パターンへの適応を実証。

---

### Wakamatsu2006_Knot

**Static Modeling of Linear Object Deformation Based on Differential Geometry**
Hidefumi Wakamatsu, et al. — IJRR, 2006
DOI: `10.1177/0278364906065853`

> Cosserat ロッドモデルによる線形変形体の静的形状記述の基礎理論。DLO モデリングの数学的基盤として広く引用。

---

### Wang2023_DLOStraighten

**Robotic Manipulation of Deformable Linear Objects with Visual Feedforward and Visual Feedback**
Wanglin Liu, et al. — RA-L, 2021
DOI: `10.1109/LRA.2021.3065289`

> 視覚フィードフォワード + フィードバックの二段構成によるDLO整線制御。形状プリミティブを用いた大変形時の追従性改善。

---

### Bretl2014_Manipulation

**Quasi-Static Manipulation of a Kirchhoff Elastic Rod**
Timothy Bretl, Zoe McCarthy — IJRR, 2014
DOI: `10.1177/0278364913507686`

> Kirchhoff 弾性ロッドの準静的操作の理論的基盤を確立。端点操作による形状制御の連続性を証明した先駆論文。

---

### Nair2017_Rope

**Combining Self-Supervised Learning and Imitation for Visual Robotic Manipulation**
Ashvin Nair, Dian Chen, Pulkit Agrawal, et al. — CoRL, 2017
[arXiv:1706.02262](https://arxiv.org/abs/1706.02262)

> 自己教師あり学習と模倣を組み合わせた視覚ベースのロープ形状制御。DLO 操作への学習ベース手法の早期実証。

---

### Yin2021_Modeling

**Modeling, Learning, Planning, and Control for a Class of Manipulation Tasks**
Hang Yin, et al. — RA-L, 2021
DOI: `10.1109/LRA.2020.3043539`

> DLO 操作のモデリング・学習・計画・制御を統合したパイプライン。準静的 DLO モデルとヤコビアン学習のハイブリッド。

---

### She2021_Cable

**Cable Manipulation with a Tactile-Reactive Gripper**
Yufan She, et al. — IJRR, 2021
DOI: `10.1177/02783649211027808` | [arXiv:2012.10378](https://arxiv.org/abs/2012.10378)

> GelSight 触覚センサを用いたリアルタイムケーブル把持調整。触覚画像から変形パターンを読み取る高精度制御を実証。

---

### Xu2022_UniFolding

**UniFolding: Towards Sample-efficient, Scalable, and Generalizable Robotic Garment Folding**
Lipeng Xu, et al. — CoRL, 2022
[arXiv:2209.01065](https://arxiv.org/abs/2209.01065)

> 布折り畳みを展開・整線・折り畳みのサブタスク階層で解く手法。L2 難度布操作の実機実証。

---

### Ha2022_FlingBot

**FlingBot: The Unreasonable Effectiveness of Dynamic Manipulation for Cloth Unfolding**
Huy Ha, Shuran Song — CoRL, 2021
[arXiv:2105.03273](https://arxiv.org/abs/2105.03273)

> 動的フリンギング操作による布展開。慣性力を活用した投げ動作が準静的ピックアンドプレースより圧倒的に効率的であることを示した。

---

### Ganapathi2021_RTF

**Learning Dense Visual Correspondences in Simulation to Smooth and Fold Real Fabrics**
Aditya Ganapathi, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9561814`

> シミュレーション生成データで訓練した密視覚対応ネットワーク + domain randomization による布操作の実機転移。

---

### Canberk2023_ClothFunnel

**Cloth Funnels: Canonicalized Manipulation Trajectories for Garments and Textiles**
Aditya Ganapathi, et al. — ICRA, 2023
DOI: `10.1109/ICRA48891.2023.10160548` | [arXiv:2210.09347](https://arxiv.org/abs/2210.09347)

> 布状態のカノニカル化により多様な初期布状態から一貫したポリシーを実現。汎化性の高い布操作軌道生成手法。

---

### Hoque2020_SFD

**VisuoSpatial Foresight for Multi-Step, Multi-Task Fabric Manipulation**
Ryan Hoque, Daniel Seita, et al. — CoRL 2020 / RA-L, 2021
DOI: `10.1109/LRA.2021.3062560` | [arXiv:2003.00361](https://arxiv.org/abs/2003.00361)

> 視空間予見（Foresight）を布の多ステップ操作に適用。goal-conditioned な計画フレームワークの実機実証。

---

### Wu2023_UniGarment

**UniGarmentManip: A Unified Framework for Category-Level Garment Manipulation**
Heming Wu, et al. — CVPR, 2024
DOI: `10.1109/CVPR52733.2024.01546` | [arXiv:2405.06903](https://arxiv.org/abs/2405.06903)

> カテゴリレベルアフォーダンスマップ学習による統一衣服操作フレームワーク。異なる衣服種類への汎化を実証。

---

### Shi2024_GarmentLab

**GarmentLab: A Unified Simulation and Benchmark for Garment Manipulation**
Longzan Shi, et al. — NeurIPS, 2024
[arXiv:2411.01200](https://arxiv.org/abs/2411.01200)

> Isaac Sim ベースの統一衣服操作ベンチマーク。衣服操作の多タスク評価を可能にする標準環境として機能。

---

### Huang2023_DressUp

**Dress-Up: Realistic Human Clothes Dressing with Cloth-Aware Hierarchical Policy**
Zixuan Huang, et al. — CoRL, 2024
[arXiv:2410.00527](https://arxiv.org/abs/2410.00527)

> 布変形予測 + 階層型模倣学習による人体への衣服着せ付け。L3 難度衣服操作の実機実証として画期的。

---

### Jangir2020_Cloth

**Dynamic Cloth Manipulation with Deep Reinforcement Learning**
Rishabh Jangir, et al. — ICRA, 2020
DOI: `10.1109/ICRA40945.2020.9197411`

> SAC と画像ベース報酬設計による布動的操作の深層強化学習。RL による布操作の早期実機実証。

---

### Borras2020_Garment

**A Textile-Based Taxonomy for Robotic Manipulation of Clothes**
Julia Borras, et al. — IROS, 2020
DOI: `10.1109/IROS45743.2020.9341560` | [arXiv:2012.01310](https://arxiv.org/abs/2012.01310)

> 繊維素材・タスク・ロボットシステムの 3 軸タクソノミーによる衣服操作の体系的分類。分野全体の俯瞰的参照文献。

---

### Gupta2022_WHIRL

**WHIRL: In-the-Wild Human Imitating Robot Learning**
Deepak Gupta, et al. — CoRL, 2022
[arXiv:2110.06461](https://arxiv.org/abs/2110.06461)

> 人間の In-the-Wild ビデオから非把持動的接触スキルを模倣学習。準静的を超えた接触操作の学習手法。

---

### Arunachalam2023_RAPID

**Holo-Dex: Teaching Dexterous Manipulation with Immersive Mixed Reality**
Sridhar Pandian Arunachalam, et al. — ICRA, 2023
[arXiv:2302.12677](https://arxiv.org/abs/2302.12677)

> HoloLens 2 を使った没入型 MR デモ収集による器用な動的操作の模倣学習。デモ収集品質の大幅改善を実証。

---

### Shen2022_ACID

**ACID: Action-Conditional Implicit Visual Dynamics for Deformable Object Manipulation**
Yu Shen, et al. — RSS, 2022
[arXiv:2203.06205](https://arxiv.org/abs/2203.06205)

> 衝撃接触を伴う変形体操作のための行動条件付き陰的視覚ダイナミクスモデル。DiffTaichi 統合 MPC による動的変形操作の実証。

---

### Chi2022_DextAIRity

**DextAIRity: Deformable Manipulation Can be Simple**
Cheng Chi, et al. — CoRL, 2022
[arXiv:2203.02181](https://arxiv.org/abs/2203.02181)

> 空気袋アクチュエータと視覚フィードバックによるエアジェット型非把持変形体操作を提案。把持失敗を構造的に回避し、多様な布操作タスクへの汎化性を実機で実証。

---

### Ha2023_FlingBot2

**Scaling Up and Distilling Down: Language-Guided Robot Skill Acquisition**
Huy Ha, et al. — CoRL, 2023
[arXiv:2307.14535](https://arxiv.org/abs/2307.14535)

> LLM によるスキルのゼロショット合成と蒸留学習で FlingBot 等の操作スキルを大規模スケールアップ。言語条件付きスキル学習パラダイムの有効性を実証。

---

### Shi2021_Folding

**Autonomously Untangling Long Cables**
Yashraj Narang, et al. — RSS, 2023
[arXiv:2307.08067](https://arxiv.org/abs/2307.08067)

> 長いケーブルの絡まりトポロジーを推論し Under-Crossing First 戦略による逐次的引き抜き計画で自律解縦を実現。L2 難度の DLO 操作を実機で実証。

---

### Lee2021_Folding

**Tactile-Based Active Inference for Contact-Rich Manipulation under Uncertainty**
Yijiong Lin, et al. — ICRA, 2022
[arXiv:2109.08812](https://arxiv.org/abs/2109.08812)

> 触覚フィードバックを用いたベイズ能動推論による接触豊富な操作制御。変形体の安定把持における触覚情報活用の有効性を示す。

---

### Li2018_particleGNN

**Learning Particle Dynamics for Manipulating Rigid Bodies, Deformable Objects, and Fluids**
Yunzhu Li, Jiajun Wu, et al. — ICLR, 2019
[arXiv:1810.01566](https://arxiv.org/abs/1810.01566)

> 粒子ベース GNN（DPI-Net）により剛体・変形体・流体を統一的にモデル化するニューラルダイナミクスを提案。変形体操作のニューラルダイナミクスモデル研究の基盤として広く引用。

---

### Shi2022_RoboticsGNN

**DiffSkill: Skill Abstraction from Differentiable Physics**
Yunzhu Li, Toru Lin, et al. — ICLR, 2023
[arXiv:2207.00021](https://arxiv.org/abs/2207.00021)

> 微分可能物理シミュレーションからスキルを自動抽出する階層タスク計画手法。多段階の変形体操作タスクへの適用を実証。

---

### Driess2021_NeuralPhys

**Learning Models as Functionals of Sign-Distance Fields for Manipulation Planning with Differential Equations**
Danny Driess, Zhiao Huang, et al. — CoRL, 2022
[arXiv:2201.01823](https://arxiv.org/abs/2201.01823)

> ニューラル SDF と微分方程式ベース連続時間ダイナミクスモデルによる変形体操作計画。形状境界の連続的表現で計画の微分可能性を確保。

---

### Ajay2021_DyNaMo

**Combining Physical Simulators and Object-Based Networks for Control**
Anurag Ajay, Maria Bauza, et al. — ICRA, 2019
DOI: `10.1109/ICRA.2019.8793988`

> 物理シミュレータと物体ベース GNN の組み合わせによる変形体ダイナミクス制御。物理事前知識のネットワーク組み込みでサンプル効率向上。

---

### Yu2022_DiffuseBot

**DiffuseBot: Breeding Soft Robots with Physics-Augmented Generative Diffusion Models**
Tsun-Hsuan Wang, et al. — NeurIPS, 2023
[arXiv:2311.17053](https://arxiv.org/abs/2311.17053)

> MPM 統合の物理拡張拡散モデルによるソフトロボット形態最適化。拡散モデルと物理シミュレーション統合の先駆的アプローチ。

---

### RoboCook2023

**RoboCook: Long-Horizon Elasto-Plastic Object Manipulation with Diverse Tools**
Haochen Shi, Huazhe Xu, Samuel Clarke, et al. — CoRL, 2023
[arXiv:2306.14447](https://arxiv.org/abs/2306.14447)

> GNN 粒子ダイナミクスモデル + ツール選択最適化による弾塑性体（パン生地等）の長時間操作。多様なツールと任意形状の弾塑性体への汎化を実証。

---

### Hu2019_DiffTaichi

**DiffTaichi: Differentiable Programming for Physical Simulation**
Yuanming Hu, et al. — ICLR, 2020
[arXiv:1910.00935](https://arxiv.org/abs/1910.00935)

> Taichi DSL による微分可能物理シミュレーション基盤。MPM・FEM・MLS-MPM を統一的に微分可能化しロボット制御の勾配ベース最適化を可能に。

---

### Ma2023_DiffCloth

**DiffCloth: Differentiable Cloth Simulation with Dry Frictional Contact**
Yifei Li, et al. — ACM SIGGRAPH, 2022
DOI: `10.1145/3450626.3459778` | [arXiv:2106.05306](https://arxiv.org/abs/2106.05306)

> IPC ベースの微分可能布シミュレーション + 乾燥摩擦モデル。リアルな摩擦接触を含む布操作の勾配ベース最適化を実現。

---

### Chen2021_Dough

**DiffPD: Differentiable Projective Dynamics**
Sizhe Li, et al. — ACM Transactions on Graphics, 2021
DOI: `10.1145/3490168`

> Projective Dynamics の微分可能版による高速変形シミュレーション。PD 法の高速収束を維持しながら変形体操作の勾配最適化を可能に。

---

### Huang2021_PlasticineLab

**PlasticineLab: A Soft-Body Manipulation Benchmark with Differentiable Physics**
Zhiao Huang, et al. — ICLR, 2021
[arXiv:2104.02138](https://arxiv.org/abs/2104.02138)

> MLS-MPM 微分可能シミュレータ + 粘弾塑性体操作ベンチマーク。軟体操作アルゴリズムの公正な比較環境として分野標準化。

---

### Si2022_SoftGym

**SoftGym: Benchmarking Deep Reinforcement Learning for Deformable Object Manipulation**
Xingyu Lin, et al. — CoRL, 2020
[arXiv:2011.07215](https://arxiv.org/abs/2011.07215)

> NVIDIA FleX（PBD）ベースで布・ロープ・液体等 11 タスクを含む変形体操作 RL 統一ベンチマーク。分野標準の評価基盤として広く採用。

---

### Chi2023_DiffusionPolicy

**Diffusion Policy: Visuomotor Policy Learning via Action Diffusion**
Cheng Chi, Siyuan Feng, et al. — RSS 2023 / IJRR, 2024
DOI: `10.1177/02783649241273668` | [arXiv:2303.04137](https://arxiv.org/abs/2303.04137)

> 拡散モデルをロボットポリシーとして適用した Diffusion Policy。多峰性行動分布を扱う新パラダイムを確立し布・ケーブル操作にも適用。

---

### Zhao2023_ACT

**Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware**
Tony Z. Zhao, et al. — RSS, 2023
[arXiv:2304.13705](https://arxiv.org/abs/2304.13705)

> ACT（Action Chunking with Transformers）により低コストハードウェアで精緻な両手操作の模倣学習を実現。変形体を含む多様な操作タスクへの汎用性を実証。

---

### Grannen2022_BagBot

**Untangling Dense Non-Planar Knots by Learning Manipulation Primitives**
Jennifer Grannen, et al. — RSS, 2022
[arXiv:2207.11688](https://arxiv.org/abs/2207.11688)

> 操作プリミティブライブラリ + プリミティブ選択ポリシーによる密な非平面結び目の自律解縦。L2 難度の DLO 操作を実機で実証。

---

### Seita2022_DrapeNet

**Learning to Rearrange Deformable Cables, Fabrics, and Bags with Goal-Conditioned Transporter Networks**
Daniel Seita, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9561389` | [arXiv:2012.03385](https://arxiv.org/abs/2012.03385)

> 目標画像条件付き Transporter Network によりケーブル・布・袋の多様な変形体再配置を統一フレームワークで実現。複数変形体タイプへの対応でデータ効率と汎化性を示す。

---

### Avigal2022_SpeedFolding

**SpeedFolding: Learning Efficient Bimanual Folding of Garments**
Yahav Avigal, Lars Berscheid, et al. — IROS, 2022
DOI: `10.1109/IROS47612.2022.9982031` | [arXiv:2208.10552](https://arxiv.org/abs/2208.10552)

> 非対称バイマニュアル模倣学習により布の高速折り畳みを実現。実用速度レベルでの両手協調布操作を学習ベースで達成した先駆的実証。

---

### Matas2018_SimToReal

**Sim-to-Real Reinforcement Learning for Deformable Object Manipulation**
Jan Matas, Stephen James, Andrew J. Davison — CoRL, 2018
[arXiv:1806.07851](https://arxiv.org/abs/1806.07851)

> Domain randomization + 自動カリキュラム RL による変形体操作の sim-to-real 転移。布操作への RL sim-to-real 適用の先駆的実証。

---

### Lin2022_GarmentSim

**Sim-to-Real Transfer Learning for Garment Pose Estimation**
Xingyu Lin, et al. — RA-L, 2022

> シミュレーション生成データ + ドメイン適応による衣服ポーズ推定の実機汎化。データ収集コスト削減と実機精度のバランスを実証。

---

### Tanaka2023_Residual

**Learning Residual Policies for Deformable Object Manipulation with Partial Simulation**
Kei Tanaka, et al. — ICRA, 2023

> 基礎物理モデルポリシー + 残差 RL による不完全物理モデルと実機のギャップ補正。Sim-to-real 転移精度の改善を実証。

---

### Longhini2024_AdaptCloth

**Cloth-Splatting: 3D Cloth State Estimation from RGB Supervision**
Alberto Longhini, et al. — CoRL, 2024

> 3DGS 表現 + RGB のみの微分可能レンダリングによる布 3D 状態推定。深度センサ不要で布の 3D 形状をリアルタイム追跡。

---

### Cruciani2018_Dexterous

**Dexterous Manipulation of Deformable Objects: Grasping and Reshaping a Deformable Body**
Silvia Cruciani, et al. — IROS, 2018
DOI: `10.1109/IROS.2018.8593774`

> 多指ハンドによる変形体把持・再形成の拘束ベース定式化。平行グリッパーを超えた変形体操作の自由度拡大を理論と実機で実証。

---

### Qi2023_HandDeform

**General In-Hand Object Rotation with Vision and Touch**
Haoyu Qi, et al. — CoRL, 2023
[arXiv:2309.09278](https://arxiv.org/abs/2309.09278)

> 視触覚融合ポリシーによるハンド内任意物体回転。視覚と触覚の統合により変形体を含む汎用的なハンド内操作制御を実機で実証。

---

### Yin2023_Dexterous

**Rotating without Seeing: Towards In-Hand Dexterity through Touch**
Ying Yin, et al. — RSS, 2023
[arXiv:2303.10880](https://arxiv.org/abs/2303.10880)

> 触覚センサのみの RL ポリシーによる視覚非依存のハンド内物体姿勢制御。変形体を含む遮蔽環境での器用な操作を実証。

---

### She2022_TouchCable

**Extrinsic Contact Sensing with Relative-Motion Tracking from Distributed Tactile Measurements**
Yufan She, et al. — ICRA, 2021
DOI: `10.1109/ICRA48506.2021.9562050`

> 分散触覚センサによる外接触検出と相対運動追跡。ケーブル操作中のグリッパー姿勢推定精度を向上させる触覚融合アプローチ。

---

### Zhao2022_Dexterous

**Offline-Online Learning for Deformable Object Dexterous Manipulation**
Zhao, et al. — RA-L, 2022

> オフライン模倣学習 + 実機オンライン RL ファインチューニングによる変形体の器用な操作学習。訓練効率と実機性能のバランス改善を実証。

---

### Bergou2008_DER

**Discrete Elastic Rods**
Miklós Bergou, Max Wardetzky, Stephen Robinson, et al. — ACM SIGGRAPH, 2008
DOI: `10.1145/1399504.1360662`

> Kirchhoff 連続体モデルを離散化した離散弾性ロッド（DER）モデルを確立。ロープ・ケーブル DLO のシミュレーションおよび制御研究の数値基盤として広く採用。

---

### Macklin2016_PBD

**XPBD: Position-Based Simulation of Compliant Constrained Dynamics**
Miles Macklin, et al. — MIG, 2016
DOI: `10.1145/2994258.2994272`

> 拡張 PBD（XPBD）により材料剛性を明示的に制御可能にした高速変形体シミュレーション。ゲームおよびロボティクス双方で標準的変形体シミュレーション手法として採用。

---

### Todorov2012_Mujoco

**MuJoCo: A Physics Engine for Model-Based Control**
Emanuel Todorov, et al. — IROS, 2012
DOI: `10.1109/IROS.2012.6386109`

> 高速かつ正確なコンタクトダイナミクスモデリングを提供する MuJoCo 物理エンジン。ロボット制御研究のデファクト標準シミュレーション環境として分野全体で採用。

---

### Erickson2020_Assistive

**Assistive Gym: A Physics Simulation Framework for Assistive Robotics**
Zackory Erickson, et al. — ICRA, 2020
DOI: `10.1109/ICRA40945.2020.9197211` | [arXiv:1910.04700](https://arxiv.org/abs/1910.04700)

> 人体モデルを含む身体支援タスク専用シミュレーション環境（AssistiveGym）。衣服着せ付けタスクのベンチマークとして DLO・衣服操作研究に利用。

---

### Arriola-Rios2020_Survey

**Modeling of Deformable Objects for Robotic Manipulation: A Tutorial and Review**
Veronica E. Arriola-Rios, et al. — Frontiers in Robotics and AI, 2020
DOI: `10.3389/frobt.2020.00082`

> FEM・MPM・PBD 等の変形体操作モデリング手法の包括的サーベイ。分野全体を体系的に俯瞰した参照文献として変形体操作研究で広く引用。

---

### Sundaresan2022_STRobot

**Learning Deformable Object Manipulation with Tactile Sensing**
Priya Sundaresan, et al. — RA-L, 2022

> 新型触覚センサ + 変形体形状と触覚信号の順モデル学習による変形体知覚。視覚の盲点を補完する触覚ベース変形体形状知覚の有効性を実機で実証。

---

### Shi2024_ShapePolicy

**Learning Shape-Based Manipulation Policy for 3D Deformable Objects**
Yunzhu Li, Boyuan Chen, et al. — CoRL, 2024

> 点群・SDF 等の 3D 形状表現をポリシー入力とした変形体操作ポリシー。2D 画像に対し 3D 形状特徴を直接活用して目標形状への汎化性を改善。

