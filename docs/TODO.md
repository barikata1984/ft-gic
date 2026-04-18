# TODO

## ロープシミュレーション

- [x] Isaac Sim ロープシミュレーション手法の調査
- [x] src レイアウトでの実装（`src/rope_sim/`, `scripts/`）
- [x] headless 動作確認（先端 z≈0.2m、理論値と一致）
- [x] GUI（headed）動作確認
- [ ] コンテナリビルド（Dockerfile の `/isaac-sim/kit/` chown 修正を適用）
- [ ] リビルド後のキャッシュエラー解消・アセットダウンロード確認
- [ ] より複雑なロープ変形シミュレーション（外力付与・障害物との接触等）
