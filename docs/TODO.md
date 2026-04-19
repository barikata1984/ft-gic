# TODO

## ロープシミュレーション

- [x] Isaac Sim ロープシミュレーション手法の調査
- [x] src レイアウトでの実装（`src/rope_sim/`, `scripts/`）
- [x] headless 動作確認（先端 z≈0.2m、理論値と一致）
- [x] GUI（headed）動作確認
- [x] README をプロジェクト実態に合わせて全面改訂（実行例コマンド付き）
- [x] アンカー円運動モード実装（`--circle-radius`, `--circle-period`）
- [x] アンカー反力・トルクの解析的ログ出力実装（Newton の第二法則）
- [x] 重力・遠心力を考慮した妥当性検証（headless 実行で確認）
- [ ] コンテナリビルド（Dockerfile の `/isaac-sim/kit/` chown 修正を適用）
- [ ] リビルド後のキャッシュエラー解消・アセットダウンロード確認
- [ ] 円運動の定常状態検証（duration 30s 以上での |Fxy| 収束確認）
- [ ] より複雑なロープ変形シミュレーション（外力付与・障害物との接触等）
