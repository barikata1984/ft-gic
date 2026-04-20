# TODO

## GIC (Gaussian-Informed Continuum)

- [ ] ホスト側で `docker compose config` による YAML 構文確認
- [ ] `docker compose --profile gic build gic` でイメージビルド (60〜90 分)
- [ ] VS Code で "Reopen in Container" → ピッカーに `isaac-sim` と `gic` が表示されることを確認
- [ ] GIC devcontainer に接続し、基本動作確認スクリプトを実行
  - `python3 --version` / `nvcc --version` / `nvidia-smi`
  - `import torch` + CUDA 可用性チェック
  - `import taichi as ti; ti.init(arch=ti.cuda)`
  - CUDA 拡張 3 本 (`diff_gaussian_rasterization`, `simple_knn._C`, `pytorch3d`)
  - `import open3d, cv2, mmcv, ...` 他の pip 依存
  - `ffmpeg -version`
- [ ] `/workspace/gic/` に GIC をクローン (`git clone git@github.com:Jukgei/gic.git`)
- [ ] `python3 -c "import sys; sys.path.insert(0,'.'); import train_dynamic"` で imports が通ることを確認
- [ ] データセット準備（PAC-NeRF または Spring-Gaus を `gic/data/` 以下に配置）
- [ ] サンプルデータで学習実行 (`python train_dynamic.py -c config/... -s data/... -m output/...`)

## ロープシミュレーション

- [x] Isaac Sim ロープシミュレーション手法の調査
- [x] src レイアウトでの実装（`src/rope_sim/`, `scripts/`）
- [x] headless 動作確認（先端 z≈0.2m、理論値と一致）
- [x] GUI（headed）動作確認
- [x] README をプロジェクト実態に合わせて全面改訂（実行例コマンド付き）
- [x] アンカー円運動モード実装（`--circle-radius`, `--circle-period`）
- [x] アンカー反力・トルクの解析的ログ出力実装（Newton の第二法則）
- [x] 重力・遠心力を考慮した妥当性検証（headless 実行で確認）
- [x] D6 DriveAPI 剛性のキャリブレーション（USD 角度単位が deg のため π/180 変換を追加）
- [ ] コンテナリビルド（Dockerfile の `/isaac-sim/kit/` chown 修正を適用）
- [ ] リビルド後のキャッシュエラー解消・アセットダウンロード確認
- [x] kinematic body 円運動のレンダラー反映調査・修正（USD TranslateOp 直書き + physics_callback で根本解決）
- [x] GUI 円運動のカクカク・低速問題修正（`add_physics_callback` + `world.step(render=True)` 一本化）
- [ ] 円運動の定常状態検証（duration 30s 以上での |Fxy| 収束確認）
- [x] オフスクリーン動画録画スクリプト実装（`scripts/record_rope.py`, `scripts/run_record.sh`）
- [x] 剛性モデルを充填率 φ 方式に改修（E=1e9 固定、`--fill-factor` で I_eff 調整）
- [x] 正弦波振動録画スクリプト実装（`scripts/swing_rope.py`, `scripts/run_swing.sh`）
- [x] カメラ配置をモジュール化（`src/rope_sim/camera_utils.py` の `make_camera()`）
- [x] カメラ配置チェックスクリプト実装（`scripts/_check_camera.py`）
- [ ] より複雑なロープ変形シミュレーション（外力付与・障害物との接触等）
